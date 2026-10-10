#!/usr/bin/env python3
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Generates from the sources the parts of the manuals that describe them: the
command reference of the user manual (from the command tables, so that the
manual and the built-in 'help' never disagree) and the line counts of the
technical manual (so that its source map cannot drift away from the tree).
It also keeps the structure of both manuals in order: the numbers of the
chapters, sections, tables and figures, the contents in the sidebar and the
list of index terms shown as code (window.MANUAL_CODE_TERMS).

  tools/gen-docs.py           rewrite the generated parts of the two manuals
  tools/gen-docs.py --check   fail if a manual is out of date, if a command has
                              no chapter below, if a source file has no row in
                              the source map, if a BASIC function is not
                              documented in the manual, or if a link inside a
                              manual points to an id that does not exist,
                              or if a page of docs/ contains Italian text
                              (run by 'make test')
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANUAL = ROOT / "docs" / "User Manual.html"
DEVMANUAL = ROOT / "docs" / "Technical Manual.html"
BEGIN = "<!-- BEGIN GENERATED: command-reference (tools/gen-docs.py) -->"
END = "<!-- END GENERATED: command-reference -->"
TOC_BEGIN = "<!-- BEGIN GENERATED: contents (tools/gen-docs.py) -->"
TOC_END = "<!-- END GENERATED: contents -->"
TERMS_BEGIN = "<!-- BEGIN GENERATED: code-terms (tools/gen-docs.py) -->"
TERMS_END = "<!-- END GENERATED: code-terms -->"

# Chapter of the reference for every command. A new command must be added here:
# --check fails otherwise.
CATEGORIES = [
    ("ref-shell", "Shell and session", [
        "help", "ver", "cls", "exit", "history", "echo", "pause", "sleep", "which",
        "set", "alias", "reset", "sysinfo"]),
    ("ref-files", "Files and folders", [
        "ls", "dir", "cd", "pwd", "cat", "type", "more", "cp", "mv", "rm", "del", "mkdir", "md", "rmdir",
        "touch", "stat", "attrib", "comp", "cmp", "setsize"]),
    ("ref-text", "Text and data", [
        "grep", "head", "tail", "wc", "hexdump", "date", "time", "timezone", "parse",
        "stall", "eficompress", "efidecompress"]),
    ("ref-disks", "Volumes and disks", ["map", "vol", "dblk", "getmtc"]),
    ("ref-boot", "Boot options and UEFI variables", [
        "bootmgr", "bcfg", "var", "dmpstore", "setvar"]),
    ("ref-drivers", "Drivers and devices", [
        "drivers", "devices", "devtree", "dh", "openinfo", "connect", "disconnect", "reconnect",
        "load", "unload", "drvdiag", "drvcfg"]),
    ("ref-hw", "Hardware and firmware", [
        "memmap", "dmem", "mm", "pci", "smbiosview", "acpiview", "cpuid", "mode", "gop",
        "sermode", "loadpcirom"]),
    ("ref-net", "Network", ["ifconfig", "ifconfig6", "ping", "ping6", "tftp", "http"]),
    ("ref-editors", "Editors", ["edit", "hexedit"]),
]

MACROS = {}


def load_macros():
    for line in (ROOT / "src/core/shell.h").read_text().splitlines():
        m = re.match(r'#define\s+(\w+)\s+"([^"]*)"', line)
        if m:
            MACROS[m.group(1)] = m.group(2)


TOKEN = re.compile(r'\s+|//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|[A-Za-z_]\w*|\d+|.', re.S)


def c_string(lit):
    """Decodes one C string literal (without the quotes)."""
    out, i = [], 0
    esc = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'", "r": "\r", "0": "\0"}
    while i < len(lit):
        c = lit[i]
        if c == "\\":
            i += 1
            if lit[i] == "x":
                m = re.match(r"[0-9a-fA-F]+", lit[i + 1:])
                out.append(chr(int(m.group(0), 16)))
                i += 1 + len(m.group(0))
                continue
            out.append(esc[lit[i]])
        else:
            out.append(c)
        i += 1
    return "".join(out)


def tokens(text):
    for m in TOKEN.finditer(text):
        t = m.group(0)
        if t.isspace() or t.startswith("//") or t.startswith("/*"):
            continue
        yield t


def table_entries(text, typename):
    """Entries of every 'static const TYPE name[] = { {...}, ... };' in text,
    each as a list of fields; adjacent string literals are joined."""
    result = []
    for m in re.finditer(r"static const %s \w+\[\] = \{" % typename, text):
        toks = list(tokens(text[m.end():text.index("};", m.end()) + 1]))
        i = 0
        while i < len(toks) and toks[i] == "{":
            i += 1
            fields, cur = [], None
            while toks[i] != "}":
                t = toks[i]
                if t.startswith('"'):
                    cur = (cur or "") + c_string(t[1:-1])
                elif t in MACROS and cur is not None:
                    cur += MACROS[t]
                elif t == ",":
                    fields.append(cur)
                    cur = None
                else:
                    cur = t if cur is None else cur + t
                i += 1
            fields.append(cur)
            result.append(fields)
            i += 1
            if i < len(toks) and toks[i] == ",":
                i += 1
    return result


def sources():
    files = sorted((ROOT / "src").rglob("*.c"))
    return [f for f in files if f.name != "host.c"]  # host.c: test-build stubs


def commands():
    cmds = {}
    for f in sources():
        for e in table_entries(f.read_text(), "Cmd"):
            name, _fn, usage, summary = e[0], e[1], e[2], e[3]
            helptext = e[4] if len(e) > 4 and e[4] != "NULL" else ""
            flags = e[5] if len(e) > 5 else "0"
            cmds[name] = {
                "name": name, "usage": usage, "summary": summary, "help": helptext or "",
                "data": "CMD_DATA" in (flags or ""), "file": str(f.relative_to(ROOT)),
            }
    return cmds


def basic_functions():
    names = set()
    for f in sources():
        for e in table_entries(f.read_text(), "BFunc"):
            names.add(e[0])
    return sorted(names)


def lines_of(path):
    with open(path, "rb") as f:
        return sum(1 for _ in f)


def source_files():
    """The files the source map of the technical manual lists: the headers, the
    C sources of NESH, the tools and the two test programs."""
    files = set((ROOT / "include").glob("*.h"))
    files |= {p for p in (ROOT / "src").rglob("*") if p.suffix in (".c", ".h")}
    files |= {p for p in (ROOT / "tools").iterdir() if p.is_file()}
    files |= {ROOT / "tests" / "run-host-tests.sh"}
    files |= set((ROOT / "tests" / "apps").glob("*.c"))
    return {str(p.relative_to(ROOT)) for p in files}


def dir_lines(names):
    """Lines of a directory of the area table: the files it holds, and for the
    'tools, tests' row everything below them except the binary fixtures and
    the bytecode Python leaves in __pycache__, which git ignores."""
    if names == ["tools", "tests"]:
        return sum(lines_of(p) for n in names for p in sorted((ROOT / n).rglob("*"))
                   if p.is_file() and not {"fixtures", "__pycache__"} & set(p.relative_to(ROOT).parts))
    return sum(lines_of(p) for n in names for p in sorted((ROOT / n).iterdir()) if p.is_file())


# The two tables are recognised by the shape of their rows: a file in <code>
# followed by its count, and an area whose second cell names directories. Any
# other table with that shape would be rewritten too, so a numeric cell after a
# <code> cell belongs to the source map and nowhere else.
FILE_ROW = re.compile(r"(<tr><td><code>)([^<]+)(</code></td><td>)(\d+)(</td>)")
AREA_ROW = re.compile(r"(<tr><td>[^<]*</td><td>)((?:<code>[^<]+</code>(?:, )?)+)(</td><td>)([\d,]+)(</td>)")


def count_lines(text, problems):
    """Rewrites the line counts of the technical manual: the source map row by
    row, then the totals of the area table."""
    listed = []

    def file_row(m):
        path = m.group(2)
        listed.append(path)
        if not (ROOT / path).is_file():
            problems.append("%s: the source map lists '%s', which is not a file"
                            % (DEVMANUAL.name, path))
            return m.group(0)
        return m.group(1) + path + m.group(3) + str(lines_of(ROOT / path)) + m.group(5)

    def area_row(m):
        names = re.findall(r"<code>([^<]+)</code>", m.group(2))
        if not all((ROOT / n).is_dir() for n in names):
            return m.group(0)                      # not the area table
        return m.group(1) + m.group(2) + m.group(3) + format(dir_lines(names), ",") + m.group(5)

    new = AREA_ROW.sub(area_row, FILE_ROW.sub(file_row, text))
    for f in sorted(source_files() - set(listed)):
        problems.append("%s: '%s' has no row in the source map" % (DEVMANUAL.name, f))
    for f in sorted(set(listed)):
        if listed.count(f) > 1:
            problems.append("%s: the source map lists '%s' twice" % (DEVMANUAL.name, f))
    return new


def esc(s):
    return html.escape(s, quote=False)


def render(cmds):
    """The command reference. Its numbers (0.0) are set by renumber()."""
    out = [BEGIN, ""]
    for cid, title, names in CATEGORIES:
        out.append('<section class="sec" id="%s"><h3 class="h-sec">0.0 · %s</h3>' % (cid, esc(title)))
        out.append('<figure class="tbl-wrap"><table class="tbl"><thead><tr><th>Command</th><th>What it does</th></tr></thead><tbody>')
        for n in names:
            c = cmds[n]
            badge = ' <span class="badge">-data</span>' if c["data"] else ""
            out.append('<tr><td><a href="#cmd-%s"><code>%s</code></a>%s</td><td>%s</td></tr>'
                       % (n, n, badge, esc(c["summary"])))
        out.append('</tbody></table><figcaption class="cap">Table 0.0 — %s</figcaption></figure>' % esc(title))
        for n in names:
            c = cmds[n]
            out.append('<article class="cmd" id="cmd-%s" data-index="%s">' % (n, n))
            badge = ' <span class="badge" title="supports -data output">-data</span>' if c["data"] else ""
            out.append('<h4><code>%s</code>%s</h4>' % (n, badge))
            out.append('<p class="cmd-summary">%s</p>' % esc(c["summary"]))
            helptext = "\n" + esc(c["help"].rstrip("\n")) if c["help"] else ""
            out.append('<pre class="code"><span class="k">%s</span>%s</pre>' % (esc(c["usage"]), helptext))
            out.append("</article>")
        out.append("</section>")
        out.append("")
    out.append(END)
    return "\n".join(out)


NUMBERED = re.compile(r'(<span class="ch-kick">Chapter )\d+(</span>)|(<h3 class="h-sec">)\d+\.\d+( · )'
                      r'|(<figcaption class="cap">)(Table|Figure) \d+\.\d+( — )')


def renumber(text):
    """Numbers chapters, sections, tables and figures in page order: tables
    and figures are counted per chapter (Table 3.2, Figure 3.1)."""
    n = {"ch": 0, "sec": 0, "Table": 0, "Figure": 0}

    def sub(m):
        if m.group(1):
            n.update(ch=n["ch"] + 1, sec=0, Table=0, Figure=0)
            return "%s%d%s" % (m.group(1), n["ch"], m.group(2))
        if m.group(3):
            n["sec"] += 1
            return "%s%d.%d%s" % (m.group(3), n["ch"], n["sec"], m.group(4))
        n[m.group(6)] += 1
        return "%s%s %d.%d%s" % (m.group(5), m.group(6), n["ch"], n[m.group(6)], m.group(7))
    return NUMBERED.sub(sub, text)


HEADINGS = re.compile(r'<section class="chapter(?: sec)?" id="([^"]+)"[^>]*><div class="ch-head">'
                      r'<span class="ch-kick">Chapter (\d+)</span><h2 class="h-ch">(.*?)</h2>'
                      r'|<section class="sec" id="([^"]+)"[^>]*><h3 class="h-sec">(\d+\.\d+) · (.*?)</h3>', re.S)


def contents(text):
    """The contents in the sidebar, from the chapter and section headings."""
    items = []
    for m in HEADINGS.finditer(text):
        kind, ident, num, title = (("ch",) + m.group(1, 2, 3)) if m.group(1) else (("se",) + m.group(4, 5, 6))
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", title)).strip()
        items.append('<li class="toc-%s"><a href="#%s"><span class="toc-n">%s</span><span class="toc-t">%s</span></a></li>'
                     % (kind, ident, num, title))
    return '%s\n<ul class="toc-list" id="toc">\n%s\n</ul>\n%s' % (TOC_BEGIN, "\n".join(items), TOC_END)


def code_terms(text):
    """Index terms shown as code: commands, and the names of the reference
    entries (<dt>) that are not plain terms of the glossary."""
    terms = []
    for m in re.finditer(r'<(article class="cmd"|dt)(\s[^>]*)?>', text):
        attrs = m.group(2) or ""
        if 'data-kind="term"' in attrs:
            continue
        ix = re.search(r'data-index="([^"]*)"', attrs)
        for t in (ix.group(1).split(";") if ix else []):
            t = html.unescape(t.strip())
            if t and t not in terms:
                terms.append(t)
    js = json.dumps(terms, ensure_ascii=False).replace("</", "<\\/")
    return "%s\n<script>window.MANUAL_CODE_TERMS=%s;</script>\n%s" % (TERMS_BEGIN, js, TERMS_END)


def splice(text, begin, end, new, man, problems):
    a, b = text.find(begin), text.find(end)
    if a < 0 or b < 0:
        problems.append("%s: generated-section markers not found: %s" % (man.name, begin))
        return text
    return text[:a] + new + text[b + len(end):]


def structure(text, man, problems):
    """The generated parts every manual has, and the checks on its links."""
    text = renumber(text)
    text = splice(text, TOC_BEGIN, TOC_END, contents(text), man, problems)
    text = splice(text, TERMS_BEGIN, TERMS_END, code_terms(text), man, problems)
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    for target in sorted(set(re.findall(r'href="#([^"]+)"', text))):
        if target not in ids:
            problems.append("%s: link to #%s, which is not an id of the page" % (man.name, target))
    for dt in re.findall(r"<dt\b[^>]*>", text):
        if "id=" in dt and "data-index=" not in dt:
            problems.append("%s: %s has no data-index (the index would miss it)" % (man.name, dt))
    return text


def cross_links(pages, problems):
    """Links from one manual to an anchor of the other one."""
    for man, text in pages.items():
        for other, target in re.findall(r'href="((?:User|Technical)%20Manual\.html)#([^"]+)"', text):
            o = ROOT / "docs" / other.replace("%20", " ")
            if o in pages and 'id="%s"' % target not in pages[o]:
                problems.append("%s: link to %s#%s, which does not exist" % (man.name, o.name, target))


# The manuals are entirely in English (owner's decision, 4 October 2026): text,
# code, figures, diagrams and image captions. A sentence with two different words
# from ITALIAN_WORDS, or any text with one from ITALIAN_ONLY, is reported.
ITALIAN_WORDS = re.compile(
    r"\b(il|lo|gli|della|delle|degli|dello|nella|nelle|negli|sono|questo|questa|quando|perché|anche|però|oppure|"
    r"finché|ancora|sempre|niente|nessun|nessuna|dopo|ogni|tutti|tutte|viene|serve|deve|può|hanno|col|coi|dal|dai|"
    r"sul|sui|alla|alle|allo|che|non|una|del|con|si|è)\b", re.I)
ITALIAN_ONLY = re.compile(
    r"\b(della|delle|degli|dello|nella|nelle|negli|sono|questo|questa|perché|anche|però|oppure|finché|ancora|"
    r"niente|nessuna|può|è)\b", re.I)


def italian_text(page):
    """The pieces of a manual page that look Italian."""
    page = re.sub(r"<style.*?</style>|<script.*?</script>", " ", page, flags=re.S)
    attrs = " ".join(html.unescape(a) for a in re.findall(r'\b(?:alt|title|aria-label)="([^"]*)"', page))
    text = html.unescape(re.sub(r"<[^>]+>", "\n", page)) + "\n" + attrs
    found = []
    for piece in re.split(r"(?<=[.;:!?])\s+|\n", text):
        piece = piece.strip()
        if ITALIAN_ONLY.search(piece) or len({w.lower() for w in ITALIAN_WORDS.findall(piece)}) >= 2:
            found.append(piece)
    return found


def check_english(pages, problems):
    for man in pages:
        for piece in italian_text(man.read_text()):
            problems.append("%s: Italian text: %s" % (man.relative_to(ROOT), piece[:120]))


def main():
    load_macros()
    check = "--check" in sys.argv
    cmds = commands()
    problems = []
    listed = [n for _, _, names in CATEGORIES for n in names]
    for n in sorted(cmds):
        if n not in listed:
            problems.append("command '%s' (%s) has no chapter in tools/gen-docs.py" % (n, cmds[n]["file"]))
    for n in listed:
        if n not in cmds:
            problems.append("tools/gen-docs.py lists '%s', which is not a command" % n)
        if listed.count(n) > 1:
            problems.append("tools/gen-docs.py lists '%s' twice" % n)
    # 'help NAME' prints on an 80-column console
    for n, c in sorted(cmds.items()):
        for line in [c["summary"]] + c["help"].split("\n"):
            if len(line) > 78:
                problems.append("help of '%s' (%s): line longer than 78 columns: %s" % (n, c["file"], line))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    text = MANUAL.read_text()
    a, b = text.find(BEGIN), text.find(END)
    if a < 0 or b < 0:
        print("%s: generated-section markers not found" % MANUAL, file=sys.stderr)
        return 1
    new = text[:a] + render(cmds) + text[b + len(END):]
    # every BASIC function must have an entry in the function reference (<dt> of a dl.deflist)
    documented = set()
    for dt in re.findall(r"<dt[^>]*>(.*?)</dt>", new, re.S):
        for part in re.sub(r"<[^>]+>", "", html.unescape(dt)).split("\u00b7"):
            m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*\$?)", part)
            if m:
                documented.add(m.group(1).lower())
    for f in basic_functions():
        if f not in documented:
            problems.append("BASIC function %s has no entry in the function reference of %s" % (f.upper(), MANUAL.name))
    devtext = DEVMANUAL.read_text()
    devnew = count_lines(devtext, problems)
    new = structure(new, MANUAL, problems)
    devnew = structure(devnew, DEVMANUAL, problems)
    cross_links({MANUAL: new, DEVMANUAL: devnew}, problems)
    if check:
        for man, before, after in ((MANUAL, text, new), (DEVMANUAL, devtext, devnew)):
            if before != after:
                problems.append("%s is out of date: run 'make docs'" % man.relative_to(ROOT))
        check_english((MANUAL, DEVMANUAL, ROOT / "docs" / "index.html"), problems)
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1
        print("docs: %d commands, %d BASIC functions documented, %d source files counted"
              % (len(cmds), len(basic_functions()), len(source_files())))
        return 0
    for man, before, after in ((MANUAL, text, new), (DEVMANUAL, devtext, devnew)):
        if before != after:
            man.write_text(after)
            print("updated %s" % man.relative_to(ROOT))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
