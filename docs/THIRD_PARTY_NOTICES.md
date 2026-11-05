# TermOS 0.2.0 — Third-party notices

This file is the stable entry point for third-party license notices associated with the TermOS 0.2.0 build.

The package-level notice table and collected license texts are generated from the exact Buildroot build by:

```bash
python3 scripts/generate-legal-review.py \
  --legal-info build/legal-info \
  --output build/legal-review
```

The generated review bundle contains:

- `THIRD_PARTY_NOTICES.md` — target and host component inventory;
- `components.csv` — machine-readable package/version/license/source status;
- `licenses/` and `host-licenses/` — license texts collected by Buildroot;
- `source-archive-index.txt` — names and sizes of source archives collected by Buildroot;
- the original Buildroot legal-info README, manifests, and configuration.

**Important:** this generator reproduces Buildroot's declared metadata. It does not independently validate every upstream license, decide which obligations apply, or certify compliance. Do not treat an entry marked as present as proof that corresponding source is complete. The exact package-level review and durable publication of all required source and notice materials are tracked in [the v0.2.0 compliance checklist](COMPLIANCE_CHECKLIST_0.2.0.md).

The MIT license in the TermOS repository does not apply to third-party components. Each component remains subject to its own license.
