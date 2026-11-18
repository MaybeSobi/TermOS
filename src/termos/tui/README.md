# TermOS TUI Control Center

The TUI Control Center is planned after the v0.3.0 Debian foundation.

The first implementation should be a Python TUI that calls shared TermOS application interfaces. It must not own privileged system logic or become the only way to administer the system.

The CLI must remain independently usable. TUI actions must have documented CLI equivalents or stable API equivalents.
