# Security Policy

TermOS is experimental software and is not recommended for production or sensitive workloads.

## Reporting a vulnerability

Do not publish exploit details or sensitive logs in a public issue. Use GitHub's private vulnerability reporting feature if enabled for this repository. If private reporting is unavailable, contact the repository maintainer through the contact method listed on the GitHub profile and provide only the minimum information needed to coordinate a report.

## Security boundaries

- Do not run development installer code on a disk containing important data.
- Do not expose a general-purpose privileged command API.
- Validate inputs at the system-backend boundary.
- Use Debian package ownership and update mechanisms.
- Never execute remote profile scripts as root without a reviewed, explicit design.
- Keep test environments disposable when evaluating disk, boot, or privileged operations.

Security support commitments for public releases will be stated in each release. Historical Buildroot releases are not assumed to receive ongoing security updates.
