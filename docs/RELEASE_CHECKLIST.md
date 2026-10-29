# TermOS 0.1.0 — Release and Validation Checklist

This checklist records the current public release state. Mark items complete only when there is evidence for them.

## Latest local validation (2026-10-30)

- [x] Re-ran Buildroot `defconfig` so `BR2_LINUX_KERNEL_CONFIG_FRAGMENT_FILES` points to `board/termos/vm-compat.fragment`.
- [x] Reconfigured and rebuilt the kernel/ISO with VMware display and network drivers enabled in the final kernel config.
- [x] Maintainer reports the resulting ISO boots in VMware; the terminal dashboard, shell, and network connectivity work.
- [x] New local ISO SHA-256: `fdf9986af5fb7fc835e1868220385de95d3aa0bdf88672fa5a4fffec4c1336d3`.
- [ ] Upload this newly tested ISO as a new versioned release asset and verify it by downloading it back from GitHub.
- [ ] Update the README's release links and published checksum after the upload.

## Published status

- [x] Public GitHub release exists for tag `v0.1.0`.
- [x] Release describes TermOS as an experimental preview.
- [x] ISO asset is attached to the release.
- [x] GitHub reports the asset SHA-256 as `cb6d60f6dacee9ec65d4f4681bace1f5f2971673087f318dcfe5b9383e7628f7`, matching the SHA-256 recorded locally for the published ISO.
- [x] UEFI boot, dashboard, shell, and VirtIO networking were tested in QEMU (per the project test record).
- [x] Buildroot `legal-info` was generated using the same build output directory.

## Still required before promoting or redistributing the ISO more widely

- [ ] Independently download the newly published VMware-tested asset from its public release URL and run the checksum verification command from the README.
- [ ] Review `build/legal-info/manifest.csv` and the collected license texts for all target packages and relevant host tools.
- [ ] Identify and resolve the missing-source warnings in `build/legal-info/README`, including the Buildroot source code that was not saved in the legal-info output.
- [ ] Confirm the applicable license terms, required notices, and corresponding-source obligations for GPL/LGPL and other third-party components.
- [ ] Prepare and publish the required notices and source-availability information where applicable.
- [ ] Record the review outcome and the source/notice location before encouraging wider redistribution.

**Current caveat:** The ISO is already publicly downloadable. The third-party redistribution review is not complete, and the Buildroot legal-info output contains warnings about missing material. Do not treat the generated inventory as legal approval or mirror/redistribute the ISO until the applicable obligations have been reviewed and resolved.

## Optional but recommended

- [ ] Test booting from USB on real hardware.
- [ ] Test on additional physical hardware and record any compatibility issues.
- [ ] Record the host environment, test date, QEMU command, and observed results.

## Reproduce Buildroot legal information

Run this from the Buildroot source directory, using the same output directory as the TermOS build:

```bash
cd ~/TermOS/src/buildroot-2025.02.19
make O="$HOME/TermOS/build" legal-info
```

Review the generated files under `$HOME/TermOS/build/legal-info/`:

```bash
less "$HOME/TermOS/build/legal-info/README"
less "$HOME/TermOS/build/legal-info/manifest.csv"
find "$HOME/TermOS/build/legal-info" -maxdepth 2 -type f | sort
```

This release uses Buildroot 2025.02.19. If the TermOS checkout is not at `$HOME/TermOS`, replace that path with the actual project directory.

**Reminder:** A successful `legal-info` run is an inventory, not a legal-compliance certification. Review the relevant licenses and obligations before broader redistribution.
