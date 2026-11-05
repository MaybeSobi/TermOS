# TermOS 0.2.0 — Release readiness

## Verified in CI and on GitHub

- [x] TPM pytest suite is included in the required ISO workflow.
- [x] Buildroot output cache includes the complete output tree, including the target filesystem.
- [x] ISO builds successfully.
- [x] ISO reaches the init process in QEMU with UEFI firmware and VirtIO networking.
- [x] ISO format, checksum generation, and required kernel driver configuration checks pass.
- [x] TPM source modules match the corresponding copies installed in the root filesystem overlay.
- [x] No private repository signing key is included in the reviewed TPM source tree.
- [x] Buildroot legal-info generation completed successfully in workflow run #22 for the release commit.
- [x] Public v0.2.0 release includes the ISO and SHA256SUMS assets; the published ISO digest matches the checksum.

## Still open

- [ ] Inspect the exact release legal-info README, target manifest, host manifest, and collected license texts.
- [ ] Resolve all unknown license fields and missing license-file warnings.
- [ ] Review exact third-party license terms and package versions.
- [ ] Verify source and patch completeness for every applicable corresponding-source obligation.
- [ ] Collect and include Buildroot 2025.02.19 source and any required build-system patches/scripts.
- [ ] Verify toolchain source and host-tool obligations.
- [ ] Publish a durable source-and-notices package for the exact release.
- [ ] Confirm contributor rights and license coverage for all TermOS-authored files.
- [ ] Test the published ISO from USB on physical hardware.

## Release caveat

The successful QEMU boot and legal-info generation are build evidence, not legal approval. The v0.2.0 ISO is already published as an experimental preview, but the package-level redistribution review and durable corresponding-source publication are not complete. See [the detailed license review](THIRD_PARTY_LICENSE_REVIEW_0.2.0.md) and [the compliance checklist](COMPLIANCE_CHECKLIST_0.2.0.md).
