# TermOS 0.2.0 — Release, licensing, and validation checklist

This checklist distinguishes evidence that CI generated successfully from obligations that still require review. Do not mark a legal obligation complete based only on the existence of Buildroot legal-info output.

## Verified against the v0.2.0 tag

- [x] The v0.2.0 Git tag points to commit 14e0173e354a44b640723755b28180a1c819af05.
- [x] Main-branch CI run #22 for that exact commit completed successfully.
- [x] ISO build, checksum generation, kernel configuration checks, and QEMU UEFI boot to init passed in run #22.
- [x] Buildroot legal-info completed and produced README and manifest.csv.
- [x] CI recorded 61 package collection entries and 86 successful license-file hash checks. These are collection counts, not a legal conclusion.
- [x] The release ISO SHA-256 was checked against the GitHub release asset digest: 4b09ad178f3eaf202ab4e26a1c6b60c83eb4d869074de4352e1be92ba56da565.
- [x] The repository MIT license applies to TermOS-authored project files only, not third-party components.

## Remaining legal review

- [ ] Inspect target and host manifests separately; identify unknown license/version fields.
- [ ] Inspect legal-info README and resolve or document missing-material warnings, including the Buildroot source warning.
- [ ] Compare license declarations with actual license texts, exceptions, dual licensing, and embedded notices.
- [ ] Identify corresponding source, patches, and build/install scripts for distributed copyleft components.
- [ ] Verify durable source access for the exact tagged build.
- [ ] Publish required third-party notices, license texts, source links or written-offer information, and checksums.
- [ ] Review whether the repository-wide MIT declaration accurately covers all TermOS-authored files and contributions.
- [ ] Obtain independent legal review before claiming legal certification or full compliance.

## Physical hardware validation

- [ ] Boot the exact v0.2.0 ISO from USB on physical x86_64 hardware.
- [ ] Record device model, firmware mode, boot result, display, keyboard, storage, and network observations.
- [ ] Test additional physical hardware before making broad compatibility claims.

## Current status

The v0.2.0 ISO is published. Passing CI and generating Buildroot legal-info do not prove legal compliance. The actual manifests, README warnings, and source obligations require review. This document is an engineering review record, not legal advice, a formal legal opinion, or a compliance certificate.
