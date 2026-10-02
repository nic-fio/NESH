# Copyright and third-party notices

NESH — the New EFI Shell
Copyright (c) 2026 Nicola Fiorillo. All rights reserved.

NESH is **freeware**, released under the **NESH Freeware Licence**. See
[LICENSE](LICENSE).

## In short

| You may, free of charge | You may not, without a written licence |
|---|---|
| Use NESH for anything, at home or at work, also as a tool in paid work (repairing a computer, administering the machines of a company) | **Sell** NESH, or charge a fee for it |
| Copy it and give it to anyone, unchanged, with the licence | **Include** it in a product or service that is sold or offered as part of a business: an operating system, firmware, hardware, pre-installed software, a paid service |
| Sign `nesh.efi` with your own Secure Boot keys, rename it, put it on any disk and add boot entries for it | **Modify** it, or decompile it beyond what the law allows |
| Put it in a collection of tools given away free of charge (a rescue disk, a software repository), unchanged and with the licence | Remove the copyright and licence notices, or use the name NESH to suggest an endorsement |

**Want to include NESH in a product, or buy the project?** Write to
**nesh@nicfio.it**.

Versions up to and including 0.2.1 were released under the Apache License 2.0
with the Commons Clause (`LICENSE-0.2.1-and-earlier`); copies of those versions
keep that licence.

## Third-party components in this repository

| Component | Licence |
|---|---|
| `docs/assets/vendor/mermaid.min.js` (diagrams in the manuals) | MIT, see `docs/assets/vendor/mermaid.LICENSE` |
| `tests/fixtures/edk2/*.efi`, `tests/fixtures/netdrv/*.efi` (test binaries only, not part of NESH) | BSD-2-Clause-Patent, see `tests/fixtures/EDK2-License.txt` and `tests/fixtures/README.md`; `Hash2DxeCrypto.efi` also contains OpenSSL code (Apache-2.0) |

These components keep their own licences: the terms above apply to NESH itself,
not to them.
