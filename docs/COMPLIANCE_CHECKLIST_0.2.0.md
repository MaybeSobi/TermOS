# TermOS 0.2.0 — Compliance and release checklist

**Release:** 0.2.0  
**Release tag:** `v0.2.0`  
**Release commit:** `14e0173e354a44b640723755b28180a1c819af05`  
**Build system:** Buildroot 2025.02.19  
**Kernel:** Linux 6.12.27

This checklist distinguishes build evidence from legal conclusions. A successful CI job or generated inventory is not a legal approval.

## Confirmed release and build evidence

- [x] Public GitHub release `v0.2.0` exists and is neither a draft nor a prerelease.
- [x] Release includes `TermOS-CI-x86_64.iso` and `SHA256SUMS`.
- [x] SHA-256 recorded for the ISO: `4b09ad178f3eaf202ab4e26a1c6b60c83eb4d869074de4352e1be92ba56da565`; it matches the digest reported for the GitHub release asset.
- [x] Buildroot `make legal-info` completed successfully in CI for the release commit (workflow run #22).
- [x] Full CI legal-info archive was retained as a workflow artifact for inspection (14-day artifact retention at the time of the run).

## Third-party license and source review

- [ ] Inspect the exact `README`, `manifest.csv`, and `host-manifest.csv` from the v0.2.0 build.
- [ ] Review every target package's declared license against the upstream license text for the exact package version.
- [ ] Review host/build-time packages separately and decide which host components are relevant to any distributed tools or source bundle.
- [ ] Resolve every unknown license, missing license-file field, and legal-info warning.
- [ ] Identify every component for which source, notices, attribution, patent terms, relinking materials, or other additional conditions apply.
- [ ] Verify source archives, Buildroot-applied patches, kernel configuration, and build/install scripts for each corresponding-source obligation.
- [ ] Collect Buildroot 2025.02.19 source separately; Buildroot documents that its own source is not normally collected by `legal-info`.
- [ ] Review internal toolchain/compiler/runtime source and notices; do not assume that a successful build automatically supplies all toolchain source obligations.
- [ ] Generate and inspect per-component third-party notices and preserve the actual license texts.
- [ ] Publish a durable v0.2.0 source-and-notices package or a legally sufficient source-availability method, with stable links and version identifiers.
- [ ] Confirm that the MIT notice in the repository covers all TermOS-authored files and that contributors had the rights to license their contributions under MIT.
- [ ] Obtain qualified legal review for any unresolved interpretation before representing the ISO as legally cleared.

## Hardware validation

- [ ] Boot the exact published v0.2.0 ISO from USB on physical x86_64 hardware.
- [ ] Record machine model, firmware mode, date, display, keyboard, storage, and network results.
- [ ] Test at least one physical network adapter and record the driver/device identity.
- [ ] Record failures and limitations; do not generalize from one machine to all hardware.

## Release decision

**Current decision: experimental preview; third-party redistribution review is not complete.**

Do not mark the source/notice review complete until the package-level evidence above is checked and the required materials are made durably available. The v0.2.0 ISO is already public; this checklist records the work still required to support wider redistribution and a stronger compliance statement.

## Reproduction

From the TermOS project root:

```bash
./scripts/build.sh
make -C src/buildroot-2025.02.19 O="$PWD/build" legal-info
python3 scripts/generate-legal-review.py \
  --legal-info build/legal-info \
  --output build/legal-review
```

See [Third-party license review](THIRD_PARTY_LICENSE_REVIEW_0.2.0.md) and [Third-party notices index](THIRD_PARTY_NOTICES.md).

## References

- [Buildroot manual — legal notices and licensing](https://buildroot.org/downloads/manual/manual.html#legal-notice-and-licensing)
- [Buildroot 2025.02.19 source archive](https://buildroot.org/downloads/buildroot-2025.02.19.tar.xz)
