# NESH landing page — brief for the mockups

Twenty mockups of the same landing page, **same content, twenty visual directions**.
They are for choosing a direction: the chosen one becomes the real page at
`https://nesh.nicfio.it` later. The method is the one used for RootSpeak on 1 October 2026.

## Rules (all mockups)

- One **self-contained HTML file** per mockup: `site/mockups/NN-slug.html`. No JavaScript,
  no external requests (no CDN, no Google Fonts, no remote images): CSS in a `<style>`,
  images inline as `data:` URIs, fonts embedded as `data:` URIs from `/usr/share/fonts`
  if used (subset them with `pyftsubset` if available, to keep files small), or only
  system font stacks. Local fonts available: Cantarell, Quicksand, URW Gothic, P052
  (Palatino-like), C059 (Century-like), URW Bookman, Nimbus Sans, DejaVu Sans/Serif/Sans
  Mono, Liberation Sans/Serif/Mono, Noto Mono. They are for exploring only: the real site
  will use fonts licensed for the web.
- English only. Elegant, professional, appealing — a page an engineer trusts and wants to
  try. Responsive: it must look right at 1440 px and at 390 px (phone), with no horizontal
  scrolling of the page.
- **The logo** (never redrawn, never recoloured): `_shared/nesh-logo-transparent.png`
  (700×216, the whole logo with «NESH» and «THE NEW EFI SHELL», transparent background,
  dark-blue text: on dark backgrounds put it on a light plate or card) and
  `_shared/nesh-mark.png` (273×216, only the monitor with «UEFI», transparent: works on
  light and dark). On dark backgrounds you may use the mark next to the word **NESH**
  written in the page's font in a light tone. Logo colours: blues from #0a2a6b to #1e88ff,
  teal-green #2bb59a to #9be38a. The palette of the page is free.
- **The real session**: `_shared/nesh-demo.gif` (800×432, 36 KB) is a real recording in
  QEMU: `ver`, `map`, the example scripts, and a menu written in NESH BASIC listing the
  firmware boot entries. Use it (inline as `data:image/gif`) in a frame of your design.
- **Only true statements.** Use the facts below; do not invent features, users,
  testimonials, numbers, benchmarks, logos of companies, or claims of hardware support.
  Do not write «fast», «lightweight», «production-ready», «battle-tested», «trusted by».
- Program texts are quoted **exactly** as below (verbatim from NESH and its manual).
  Do not make up command output: use only the sessions below.

## What NESH is

**NESH, the New EFI Shell**: a modern command shell for UEFI firmware, with a real
scripting language. One file, `nesh.efi`: nothing to install, one signature for Secure
Boot, no EDK2 code. It runs on UEFI x86-64 firmware.

For people who work below the operating system: system administrators, firmware and
BIOS enthusiasts, those who repair boot problems, test hardware, or automate tasks
before an OS starts.

Tagline ideas (choose or adapt, keep them true): «The shell your firmware deserves.» —
«A modern shell for UEFI, in one file.» — «Before the OS, a real shell.» —
«Script your firmware in BASIC.»

## Highlights (all true today, version 0.2.1)

- **The UEFI Shell command set, rewritten from scratch**: files, disks, UEFI variables,
  drivers and devices, PCI/SMBIOS/ACPI, memory, network (IPv4 and IPv6: `ifconfig`,
  `ping`, `tftp`, `http`), editors (`edit`, `hexedit`). UEFI Shell options are accepted too.
  More than 80 commands are documented in the user manual.
- **NESH BASIC** scripts (`.nsb`): variables, loops, `SUB`/`FUNCTION`, strings, arrays,
  menus, files, and `RUN`/`RUN$` to drive commands. More than 50 built-in functions.
- **Script-friendly output**: `-data` prints `key=value` records that scripts read with
  `RECORDS` and `FIELD$`.
- **Safe boot management** with `bootmgr`: dry run, confirmation, automatic backups,
  check for missing files. `bcfg` is there too.
- **Runs UEFI Shell applications**: NESH implements `EFI_SHELL_PROTOCOL` 2.2.
- **Friendly prompt**: history with search, Tab completion, aliases, BASIC at the prompt.
- **Secure Boot aware**: low-level hardware writes are disabled while Secure Boot is
  active; reading stays allowed.
- **One file**: everything is built in, `nesh.efi` is about 363 KB. No EDK2 code: every
  command was rewritten from scratch.

## Exact sessions (use these, verbatim)

Start-up banner:
```
NESH 0.2.1 - New EFI Shell (UEFI)
Type 'help' for the commands, 'help basic' for the scripting language.
```
(Do not add a line about Secure Boot unless you show it as the one NESH prints when it is
active: `Secure Boot is active: low-level hardware writes are disabled.`)

The README example (a sequence of prompts, the PRINT gives `4000`):
```
fs0:\> map
fs0:\> ls -l \EFI\BOOT
fs0:\> bootmgr add fs0:\EFI\debian\shimx64.efi "Debian" -t
fs0:\> PRINT HEX$(&H1000 * 4)
4000
fs0:\> n = RECORDS(RUN$("map -data"), v$()) : PRINT n; " volumes and disks"
```

BASIC at the prompt:
```
fs0:\> PRINT HEX$(&HFF * 16)
FF0
fs0:\> n = 0
fs0:\> FOR i = 1 TO 5
...   n = n + i
... NEXT
fs0:\> PRINT n
15
```

`map` (in QEMU):
```
fs0:\> map
Volume Label                 Size      Free  Flags
fs0    QEMU VVFAT          503.7M    502.9M  ro boot
fs1    NESHWORK             31.9M     31.9M

Device Type            Size  Volume
blk0   removable          -  (no media)
blk1   disk            504M
blk2   partition       503M  fs0
blk3   disk             32M  fs1
```

`map -data` (first record):
```
fs0:\> map -data
kind=volume
volume=fs0
label=QEMU VVFAT
size=528171008
free=527351808
readonly=yes
removable=no
boot=yes
```

`sysinfo` (in QEMU):
```
fs0:\> sysinfo
Firmware: Debian distribution of EDK II (revision 0x00010000)
UEFI:     2.7
Secure Boot: inactive
CPU:      QEMU Virtual CPU version 2.5+ / GenuineIntel
Memory:   511 MiB
Console:  100 x 31
Graphics: 1280 x 800 (mode 0 of 30), frame buffer at 0x80000000
Tables:   10 configuration tables, ACPI, SMBIOS
```

`bootmgr` (in QEMU; you may drop the device-path lines on phones):
```
fs0:\> bootmgr
BootCurrent: 0001   BootNext: -   Timeout: 0 s
Ord  Id    Flg  Description
  1  0000  AH   UiApp
  2  0001  A *  UEFI Misc Device
  3  0002  A    UEFI Non-Block Boot Device
  4  0003  A    EFI Internal Shell
Flags: A active, H hidden, * current boot, N next boot. '-' in Ord: not in the boot order.
```

Network (in QEMU):
```
fs0:\> ping -n 3 10.0.2.2
Ping 10.0.2.2 16 data bytes.
16 bytes from 10.0.2.2 : icmp_seq=1 ttl=255 time=0ms
16 bytes from 10.0.2.2 : icmp_seq=2 ttl=255 time=0ms
16 bytes from 10.0.2.2 : icmp_seq=3 ttl=255 time=0ms

3 packets transmitted, 3 received, 0% packet loss
fs0:\> tftp 10.0.2.2 hello.txt fs1:\tftp.txt
Downloading hello.txt from 10.0.2.2 ...
20 bytes saved to fs1:\tftp.txt
```

A NESH BASIC script, `examples\menu.nsb` (excerpt, verbatim):
```
' menu.nsb - a maintenance menu: choose an action, do it, come back.
target$ = "fs1:"            ' where backups go

DO
  CLS
  PRINT "NESH maintenance - volume for backups: "; target$
  PRINT

  choice = MENU("What do you want to do?", _
                "Show the system|" + _
                "List the boot entries|" + _
                "Back up the boot loaders|" + _
                "Choose the backup volume|" + _
                "Leave the menu")

  SELECT CASE choice
    CASE 1
      RUN "sysinfo"
    CASE 2
      RUN "bootmgr list"
```
The examples shipped: `bootmenu.nsb`, `findefi.nsb`, `inventory.nsb`, `linuxboot.nsb`,
`menu.nsb`.

## Status — say it honestly (keep it visible, not hidden)

Version 0.2.1. Tested in QEMU with OVMF, including Secure Boot with test keys. On real
machines it has so far only been started on two — a Chuwi tablet and a server with a
Gigabyte motherboard — where the prompt came up, `dir` listed the files and NESH booted
Linux. What AMI, Insyde or Phoenix firmware makes of the rest is the project's main open
question. **Call to action**: «Tried it on a real machine? Send a hardware report» →
`https://github.com/nic-fio/NESH/issues/new?template=hardware-report.yml`. A machine where
everything worked is as useful a report as one where nothing did.
Not yet: ARM64 and IA32 builds.

## Get it (real links)

- **Download** the latest release: `https://github.com/nic-fio/NESH/releases/latest` —
  `nesh.efi` (about 363 KB) and `nesh-usb.img` (64 MB, a bootable disk image: write it to a
  USB stick and boot it). Checksums `SHA256SUMS` are published with the release.
- Write the image: `dd if=nesh-usb.img of=/dev/sdX bs=4M conv=fsync` (on Windows: Rufus,
  balenaEtcher).
- Or copy `nesh.efi` to a FAT-formatted USB stick or EFI system partition, as
  `\EFI\BOOT\BOOTX64.EFI` to boot it directly, or add a boot entry with `bootmgr add`.
  With Secure Boot active, sign it with a trusted key first (see the user manual).
- Source: `https://github.com/nic-fio/NESH`.

## Licence (free)

**Free for noncommercial use.** PolyForm Noncommercial License 1.0.0 (from the version
after 0.3.0): personal use, study, hobby projects, schools, charities and public bodies.
Commercial use, including use at work inside a company, needs a written licence: write to
nesh@nicfio.it. Version 0.3.0 keeps the NESH Freeware Licence, versions up to 0.2.1 keep
Apache 2.0 with the Commons Clause.
Say it plainly: not «open source» by the OSI definition (small print is enough).
No prices, no «Buy» buttons, no «Pro» edition.

## Sections of the page (in this order, adapt the layout)

1. Header: logo, links (Features, Scripting, Get NESH, Docs, GitHub), a «Download» button.
2. Hero: tagline, one-sentence description, two buttons («Download NESH 0.2.1» → releases;
   «Read the manual» → `User%20Manual.html`), and a visual: the demo GIF and/or a terminal
   with the start-up banner and the README example.
3. Why a new shell (short, true): one file, nothing to install, one signature for Secure
   Boot, a real scripting language instead of the old `.nsh` scripts, command set
   rewritten from scratch.
4. Features (the highlights above).
5. NESH BASIC: the script excerpt and the BASIC-at-the-prompt session; `-data` records with
   `map -data`.
6. Sessions: two or three of the exact sessions (map, sysinfo, bootmgr, network).
7. Safe by design: `bootmgr` dry run, confirmation, backups; Secure Boot aware.
8. Status and hardware reports (the honest note and the call to action).
9. Get NESH: the three ways (USB image, `nesh.efi`, build from source:
   `git clone https://github.com/nic-fio/NESH.git`, `make && make test && make qemu-test`).
10. Documentation: User Manual (`User%20Manual.html`), Technical Manual
    (`Technical%20Manual.html`), Design decisions and history
    (`https://github.com/nic-fio/NESH/blob/main/docs/decisions-and-history.md`).
11. Licence (short, as above).
12. Footer: «NESH — The New EFI Shell · Version 0.2.1 · © 2026 Nicola Fiorillo», links to
    GitHub, the manuals, the licence.

## Checking your work

Render each page with Chrome headless and look at the images before delivering:
`google-chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1440,7000 --screenshot=OUT.png file:///path/NN-slug.html`
and at `--window-size=390,12000`. Fix anything broken (overflow, overlaps, unreadable
contrast, empty areas, text cut off, code blocks breaking the phone layout — on phones let
code scroll inside its own box). Save a preview for the gallery:
`site/mockups/previews/NN-slug.png` (1440 px wide, the first 900 px:
`--window-size=1440,900`). Keep each file under 2 MB.
