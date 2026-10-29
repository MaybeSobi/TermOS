# TermOS 0.1.0 Release Checklist

This checklist separates checks already reported as passing from checks that still require evidence. Do not mark a check complete without recording its result.

## Confirmed for v0.1.0

- [x] Public GitHub release exists for tag `v0.1.0`.
- [x] Release notes describe the project as experimental.
- [x] README documents the build and QEMU runner commands.
- [x] UEFI boot, dashboard, shell, and VirtIO networking were tested in QEMU (per the project test record).

## Still required before distributing the ISO

- [ ] Run Buildroot's `legal-info` target from the same output directory used for the image build.
- [ ] Review `build/legal-info/manifest.csv` and the generated license texts for every included target package and relevant host package.
- [ ] Confirm the applicable source-code and notice obligations for GPL/LGPL and other licenses, including how corresponding source will be provided where required.
- [ ] Include the required notices and source-availability information with any binary distribution.
- [ ] Rebuild or identify the exact ISO intended for release, then calculate its SHA-256.
- [ ] Boot-test that exact ISO in QEMU after the final build.
- [ ] Upload the ISO and checksum to the GitHub release only after the licensing review is complete.
- [ ] Verify the uploaded asset and checksum by downloading the asset or checking its published metadata.

## Optional but recommended

- [ ] Test booting from USB on real hardware. This has not yet been verified.
- [ ] Record host environment, test date, QEMU command, and any known limitations.

## Buildroot legal-info commands

From the Buildroot source directory, using the same output directory as the TermOS build:

```bash
make O="$HOME/TermOS/build" legal-info
```

Then inspect:

```bash
less "$HOME/TermOS/build/legal-info/manifest.csv"
less "$HOME/TermOS/build/legal-info/legal-info.txt"
find "$HOME/TermOS/build/legal-info" -maxdepth 2 -type f | sort
```

If your TermOS checkout is not at `$HOME/TermOS`, replace that path with the actual project directory.

**Important:** A successful `legal-info` build is an inventory, not a legal approval by itself. Review the generated manifest and obligations before redistributing the ISO.
