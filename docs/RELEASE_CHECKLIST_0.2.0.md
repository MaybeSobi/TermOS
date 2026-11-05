# TermOS 0.2.0 — Release, licensing, and validation checklist

This checklist distinguishes evidence that CI generated successfully from obligations that still require review. Do not mark a legal obligation complete based only on the existence of Buildroot's `legal-info` output.

## Verified against the v0.2.0 tag

- [x] The `v0.2.0` Git tag points to commit `14e0173e354a44b640723755b28180a1c819af05`.
- [x] Main-branch CI run [#22](https://github.com/MaybeSobi/TermOS/actions/runs/42106722558) for that exact commit completed successfully.
- [x] The ISO build, checksum generation, required kernel configuration checks, and QEMU UEFI boot to init passed in run #22.
- [x] Buildroot `make legal-info` completed successfully for the tagged commit and produced `README` and `manifest.csv`.
- [x] The CI legal-info log recorded 61 package collection entries and 86 successful license-file hash checks. This is collection evidence, not a manual review of the manifest or license texts.
- [x] The release ISO's SHA-256 was independently checked against the GitHub release asset digest: `4b09ad178f3eaf202ab4e26a1c6b60c83eb4d869074de4352e1be92ba56da565`.
- [x] TermOS's repository `LICENSE` declares MIT for TermOS-authored project files only. This does not apply to third-party components.

## Remaining legal review before promoting or redistributing the ISO more widely

- [ ] Inspect the exact target `manifest.csv` and `host-manifest.csv`; identify any `unknown` license/version fields and classify target packages separately from build-only host tools.
- [ ] Inspect the contents of `legal-info/README` and resolve or document every missing-material warning. CI stdout reports: `WARNING: the Buildroot source code has not been saved`. Its relevance to the distributed ISO and reproducible source package must be explicitly assessed.
- [ ] Compare every target-package license declaration with the actual license texts, including exceptions, dual licensing, embedded third-party notices, and files not represented by the package's main license field.
- [ ] Identify the complete corresponding source, applicable patches, and build/install scripts for every copyleft component distributed in the ISO (including the kernel, BusyBox, glibc/toolchain runtime, and GRUB where applicable).
- [ ] Verify that the corresponding source for the exact tagged build is available to recipients through a durable, clearly linked location, with the source access method satisfying each component's license.
- [ ] Publish the required third-party notices, license texts, source links or written-offer information, and a checksum for the compliance bundle alongside the relevant release assets.
- [ ] Review whether the repository-wide MIT declaration accurately covers every TermOS-authored file and whether all contributors have granted the rights needed to publish those files under MIT.
- [ ] Obtain an independent legal review before describing the distribution as legally certified or fully compliant.

## Physical hardware validation

- [ ] Boot the exact v0.2.0 release ISO from USB on physical x86_64 hardware.
- [ ] Record device model, firmware/UEFI mode, boot result, display, keyboard, storage, and network observations.
- [ ] Test on additional physical hardware before making broad compatibility claims.

## Current status and caveats

The v0.2.0 ISO is already published. Passing CI and generating Buildroot's legal-info inventory do not prove legal compliance. The log identifies the Buildroot source archive as not saved; the exact manifests and README warnings still require inspection. The next CI revision exports a compact metadata artifact separately from the much larger source archive so that the actual manifests and license texts can be reviewed.

Buildroot documents that its legal-info data comes from package recipe metadata, may be incomplete or inaccurate, and must be checked before being used as a compliance delivery. The GNU GPL requires complete corresponding source or another permitted method of source provision when covered binaries are distributed; the exact method depends on the license version and distribution circumstances.

No formal legal certificate is created by this checklist. A legal opinion or certification must come from an appropriately qualified independent professional.
