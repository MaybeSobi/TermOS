#!/usr/bin/env python3

import os
import platform
import shutil
import socket
import subprocess
from pathlib import Path

VERSION = "0.2"

# ANSI terminal colors
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[90m"
WHITE = "\033[97m"


def clear():
    print("\033[2J\033[H", end="")


def color(text, shade):
    return f"{shade}{text}{RESET}"


def read_meminfo():
    data = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            data[key] = int(value.strip().split()[0]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return data


def format_bytes(value):
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(value)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024


def format_uptime():
    try:
        seconds = int(float(Path("/proc/uptime").read_text().split()[0]))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes = seconds // 60

        if days:
            return f"{days}d {hours}h {minutes}m"
        return f"{hours}h {minutes}m"
    except (OSError, ValueError, IndexError):
        return "Unavailable"


def bar(percent, width=20):
    percent = max(0, min(100, percent))
    filled = round(width * percent / 100)
    shade = GREEN if percent < 70 else YELLOW if percent < 90 else RED
    return color("#" * filled, shade) + color("-" * (width - filled), DIM)


def get_network_interfaces():
    interfaces = []
    try:
        for entry in Path("/sys/class/net").iterdir():
            name = entry.name
            try:
                state = (entry / "operstate").read_text().strip()
            except OSError:
                state = "unknown"
            interfaces.append((name, state))
    except OSError:
        pass
    return interfaces


def header():
    print(color(r"""
 _____                 ___  ____
|_   _|__ _ __ _ __ ___/ _ \/ ___|
  | |/ _ \ '__| '_ ` _ \ | | \___ \
  | |  __/ |  | | | | | | |_| |___) |
  |_|\___|_|  |_| |_| |_|\___/|____/
""", CYAN + BOLD))
    print(color(" TERMOS DASHBOARD", WHITE + BOLD)
          + color(f"  v{VERSION}", DIM))
    print(color(" Your system. Your terminal.", DIM))
    print(color("=" * 58, CYAN))


def system_panel():
    print(color("\n SYSTEM", CYAN + BOLD))
    print(f"  Host       : {socket.gethostname()}")
    print(f"  Kernel     : {platform.release()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Python     : {platform.python_version()}")
    print(f"  Uptime     : {format_uptime()}")

    print(color("\n MEMORY", CYAN + BOLD))
    mem = read_meminfo()
    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", mem.get("MemFree", 0))

    if total:
        used = total - available
        percent = used * 100 / total
        print(f"  RAM  {format_bytes(used)} / {format_bytes(total)}")
        print(f"  [{bar(percent)}] {percent:.1f}% used")
    else:
        print("  Memory information unavailable.")

    print(color("\n ROOT FILESYSTEM", CYAN + BOLD))
    try:
        usage = shutil.disk_usage("/")
        used = usage.total - usage.free
        percent = used * 100 / usage.total if usage.total else 0
        print(f"  Used {format_bytes(used)} / {format_bytes(usage.total)}")
        print(f"  [{bar(percent)}] {percent:.1f}% used")
    except OSError as exc:
        print(f"  Unavailable: {exc}")


def network_panel():
    print(color("\n NETWORK INTERFACES", CYAN + BOLD))
    interfaces = get_network_interfaces()

    if not interfaces:
        print("  No interfaces found.")
        return

    for name, state in interfaces:
        shade = GREEN if state == "up" else YELLOW
        print(f"  {name:<12} {color(state, shade)}")

    if shutil.which("ip"):
        result = subprocess.run(
            ["ip", "route"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout.strip():
            print(color("\n ROUTES", CYAN + BOLD))
            for line in result.stdout.strip().splitlines()[:5]:
                print("  " + line)


def pause():
    input(color("\n  Press Enter to return...", DIM))


def main():
    while True:
        clear()
        header()
        system_panel()
        network_panel()

        print(color("\n MENU", CYAN + BOLD))
        print("  [1] Refresh dashboard")
        print("  [2] Detailed system information")
        print("  [3] Open shell")
        print("  [0] Exit dashboard")

        choice = input(color("\n  termos> ", GREEN + BOLD)).strip()

        if choice == "1":
            continue
        elif choice == "2":
            clear()
            header()
            print(color("\n PLATFORM DETAILS", CYAN + BOLD))
            print(f"  System       : {platform.system()}")
            print(f"  Release      : {platform.release()}")
            print(f"  Version      : {platform.version()}")
            print(f"  Machine      : {platform.machine()}")
            print(f"  Hostname     : {socket.gethostname()}")
            print(f"  Python       : {platform.python_version()}")
            print(f"  Current user : {os.getenv('USER', 'unknown')}")
            pause()
        elif choice == "3":
            subprocess.call(["/bin/sh"])
        elif choice == "0":
            clear()
            print(color("TermOS Dashboard closed.", CYAN))
            break
        else:
            input(color("\n  Invalid option. Press Enter...", YELLOW))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(color("\n\nDashboard interrupted.", YELLOW))
