# TermOS 0.2.0 — Release readiness

## Verified in CI

- [x] TPM pytest suite is part of the required ISO workflow.
- [x] Buildroot output cache includes the complete output tree, including the target filesystem.
- [x] ISO builds successfully.
- [x] ISO reaches the init process in QEMU with UEFI firmware and VirtIO networking.
- [x] ISO format, checksum generation, and required kernel driver configuration checks pass.
- [x] TPM source modules match the corresponding copies installed in the root filesystem overlay.
- [x] No private repository signing key is included in the reviewed TPM source tree.

## Required before publishing the v0.2.0 ISO

- [ ] Generate and inspect the Buildroot legal-info archive from the exact release build.
- [ ] Resolve or document every missing-source warning in legal-info/README.
- [ ] Review manifest.csv and license texts for target packages and relevant host tools.
- [ ] Confirm required notices and corresponding-source obligations for GPL/LGPL and other third-party components.
- [ ] Decide and document the license for TermOS's own code; the GitHub repository currently reports NOASSERTION.
- [ ] Publish required notices and source-availability information where applicable.
- [ ] Download the final release asset independently and verify its SHA-256.
- [ ] Test booting the release ISO from USB on physical hardware, if available.

## Release caveat

The successful QEMU boot and generated legal-info inventory are not legal approval. Do not publish or encourage wider redistribution of the ISO until the missing-source warnings and applicable third-party license obligations have been reviewed and resolved.

The CI artifact is a temporary test artifact, not the official v0.2.0 release.
