# Custom Installer

The custom TermOS installer is planned for v0.5.0. This directory is an architectural placeholder, not an implemented installer.

The installer will be a separate application running from the live environment. It will not be part of live-build itself.

Mandatory safety requirements:
- Explicitly identify the target disk and partitions.
- Never format or repartition by default.
- Show the complete planned destructive changes before execution.
- Require a separate final confirmation.
- Stop when device identity or user intent is ambiguous.
- Keep an inspectable log and provide actionable failure details.
- Test only against disposable virtual disks until the workflow is proven.

Do not add disk-writing behavior here until its design, test plan, and recovery behavior have been reviewed.
