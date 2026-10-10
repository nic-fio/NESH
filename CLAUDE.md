# Working on NESH

How this project is developed: the agreements, the decisions that are settled,
and what to check before committing. A fresh clone plus this file is the whole
working context — nothing needed to continue the work lives outside the
repository.

## How we work

- **Talk to the user in Italian.** The code, the comments and the documentation
  are in English; the conversation is not.
- **Agree the design before writing code.** On a new area, propose the options
  and wait for a decision. The user stopped an early coding session precisely to
  do this.
- **One decision at a time, in plain language.** Long lists of simultaneous
  questions do not work here.
- **Verify, do not claim.** Every statement about behaviour comes from a run:
  the host tests, QEMU, a screenshot. "It should work" is not a result.
- **The documentation matters as much as the code** (user: *"un progetto serio
  dà alla documentazione la stessa importanza del codice"*). A feature is not
  done until the manual describes it.

## Settled decisions — do not reopen them

These were decided with the user and should not be proposed again unless the
user brings them up. The reasoning for each is in
[docs/decisions-and-history.md](docs/decisions-and-history.md).

| Decision | |
|---|---|
| **One `.efi` file** | Everything is built in: one signature for Secure Boot, nothing to install. |
| **BASIC-like scripting**, not a bash clone | The user chose it; commands are called from scripts with `RUN` / `RUN$()`, implicit `RUN` only at the prompt. |
| **No EDK2 code** | Every command NESH lacks is rewritten from scratch; EDK2 option letters are accepted where they do not clash. |
| **`-data` instead of `-sfo`** | `key=value` records read by `RECORDS()` / `FIELD$()`; `-sfo` errors and points at `-data`. |
| **`msr` stays out** | Reading MSRs hangs with #GP on the firmware; the user decided against it. |
| **No legacy EDK1 shell interface** | User: *"lasciamo riposare in pace il vecchiume"*. |
| **Secure Boot: reads yes, writes no** | Low-level hardware writes (`mm` on I/O and PCI config, `hexedit -m`) are refused while Secure Boot is active. The **clock and the serial port stay allowed** — the user ruled they are not a security risk. |
| **Manuals entirely in English (4 October 2026)** | Every page of `docs/` is in English, everywhere: running text, code and its comments, figures, diagrams, image captions. No Italian label in parentheses, no Italian example text. `tools/gen-docs.py --check` (in `make test`) reports any Italian it finds. |
| **Light documentation only** | No dark themes, no dark-mode media queries, no theme toggle. The code blocks are dark: that comes with the common style of the manuals, and the owner confirmed it on 1 October 2026 together with the common style. |
| **Freeware, NESH Freeware Licence (2 October 2026, D21)** | From 0.3.0: free use, also as a tool in paid work; free redistribution of the unchanged file and in free collections; Secure Boot signing allowed; no sale, no inclusion in commercial products or services, no modification, no decompilation beyond the law. Commercial licences or the sale of the project through `nesh@nicfio.it`. Versions up to 0.2.1 keep Apache 2.0 + Commons Clause (`LICENSE-0.2.1-and-earlier`). The manuals and `docs/index.html` still name the old licence in their footer: they describe 0.2.1, and change with the 0.3.0 release. |

## The repository

| Where | What |
|---|---|
| `src/core`, `src/basic`, `src/cmd` | Shell core, the BASIC interpreter, the commands. |
| `src/pal`, `src/platform` | The platform layer: `pal_efi.c` for firmware, `pal_host.c` for the Linux test build. |
| `tools/` | `elf2efi.py` (ELF &rarr; PE32+), `gen-docs.py`, `check-doc-examples.py`, `run-qemu.sh`, `mkusb.sh`, `record-demo.py`, `setup-dev.sh`, `backup.sh`. |
| `tests/` | Host tests, QEMU scripts (`tests/efi/*.nsb`) and binary fixtures (EDK2 applications, network drivers). |
| `docs/` | The two HTML manuals, the start page, the decisions log, `assets/` (Mermaid, the demo GIF). The manuals are published on the website by `site/publish.sh` (GitHub Pages was switched off on 2 October 2026, D21). |
| `logos/` | `nesh-logo.png`, the logo (PNG, 2172×724, white background). Never edited: the manuals carry a transparent, cropped copy (700 px) on their cover. |
| `examples/` | The `.nsb` scripts shipped with NESH and shown in the manual. |
| `site/` | The website, `https://nesh.nicfio.it`, on the owner's VPS (D21). `landing/index.html`: the landing page (mockup 05 «Glass», chosen on 2 October 2026), with its preview and brief. `publish.sh` builds `site/public/` (landing, the two manuals, `licence.html` made from `LICENSE` by `licence-page.py`, `download/` with the release files and checksums, `og.png`, `robots.txt`, `sitemap.xml`) and copies it to the VPS as user `progetti`; `--build` only builds. Publish together with every change to the manuals or a release. The 20 mockups stay in `site/mockups/`, outside git. |
| `build/` | Products only, never committed. |

The repository follows the standard layout shared by the seven projects (AMS,
EFI_PARTITION_MANAGER, HOSTER, MTERM, NESH, PHONESTRA, SCRAPER): `src/`,
`tests/`, `tools/`, `docs/` (with `index.html`, the two manuals, `README.md`,
`decisions-and-history.md`), `NOTICE.md`, and the common `make` targets
`all`, `test`, `docs-check`, `clean`.

## The manuals

`docs/User Manual.html` and `docs/Technical Manual.html` use the **common style
of the manuals of the seven projects**, identical in all of them: cover with
the logo, «User Manual» / «Technical Manual», version and date; sidebar with
search and contents; chapters («Chapter N»), numbered sections, tables and
figures with captions; the callouts, the code blocks with the Copy button, the
alphabetical index; one footer line. Each manual is **one self-contained HTML
file**: the common style sheet and script are embedded byte for byte (do not
change them in one project only); what only NESH needs comes after them, in a
block marked `Solo per NESH` (code-block titles, the Mermaid diagrams, which
load the local copy in `docs/assets/vendor`). The Copy button appears on blocks
whose lines start with `$ `; NESH prompts (`fs0:\>`) get no button.

`tools/gen-docs.py` writes the parts between the `GENERATED` markers (command
reference, sidebar contents, index terms shown as code) and numbers chapters,
sections, tables and figures: after adding or moving one, run `make docs`. Write
new sections as `<section class="sec" id="..."><h3 class="h-sec">0.0 · Title</h3>`
and new tables and figures with `<figcaption class="cap">Table 0.0 — ...` (or
`Figure 0.0 — ...`); `make docs` fixes the numbers. Index entries come from
`data-index` attributes.

## Before committing

1. `make test` — host tests, and the documentation checks (`make docs-check`
   runs only those): every command and
   every BASIC function must be documented, help lines stay within 78 columns,
   and the examples in the manual are run and compared against their printed
   output. **This fails if the manual is out of date**; `make docs` regenerates
   the command reference from the help texts in the C sources, and the line
   counts of the technical manual from the files themselves (a new source file
   needs its row in the source map).
2. `make qemu-test` when anything on the firmware side changed, and
   `make qemu-nettest` / `make qemu-sbtest` for network or Secure Boot work.
3. Do not report success from a pipeline that hid a failure: check the exit
   status, and in the QEMU logs the run is only a pass with `failures:0`.
4. Commits use the repository-local identity set by `tools/setup-dev.sh`, which
   keeps the personal address out of the public history.

Releases: bump `NESH_VERSION` in `src/core/shell.h` **and** the version strings
in `README.md`, `docs/index.html`, both manuals (cover, footer and the tested example
output), then tag. For 0.3.0 the footers also change licence: «Licence: NESH Freeware Licence». The annotated tag message becomes the release notes; CI
builds `nesh.efi` and publishes it. `nesh-usb.img` is uploaded by hand
(`make usb`, then `gh release upload`).

## Where the project stands

Tested in QEMU with OVMF, including Secure Boot with generated test keys.
**On real hardware, only a first smoke test** (September 2026, by the user): on a
Chuwi tablet and a server with a Gigabyte motherboard the prompt came up, `dir`
worked and NESH booted Linux — nothing else was tried, firmware vendor and
Secure Boot state were not recorded. In October 2026 the tablet showed two
defects, both fixed and confirmed there: the efifb crash of Linux booted from
NESH (D16e) and the missing cursor in `edit` (history, phase 14). Broader hardware coverage is still the
main open item, and the reason for the announcement on the OSDev forum asking
for reports. Also open:
`find`, `crc32`, `sha256`, `efiinfo`, a `secureboot` key listing,
`bootmgr scan`, `ON ERROR`; `https` and host names in `http` are untested;
ARM64 and IA32 builds do not exist yet.

## Announcements

Posted to find testers on real hardware; check them for replies and reports.

| Where | When | Link | Status |
|---|---|---|---|
| OSDev forum, Announcements | 2026-09-20 | https://forum.osdev.org/viewtopic.php?p=354826 | No replies. **Deleted by the user on 2026-10-02** (it promoted the Apache licence and the public source, see D21). |
| Win-Raid, BIOS Modding/Flashing Tools | 2026-09-23 | https://winraid.level1techs.com/t/119449 | Posted by Claude at the user's request. No replies. The forum does not let the author delete it any more: **withdrawn on 2026-10-02**, title «[Withdrawn] NESH» and a one-line notice (D21). The old text is still in the post's edit history. |

The user chose not to use Reddit. Other places considered, only if the user
brings them up again: the edk2 mailing list, ServeTheHome, Hacker News (Show
HN), Phoronix forums, Arch "Community Contributions". Claude never types
forum passwords: the user logs in.
