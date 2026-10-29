# TermOS interactive dashboard autostart
if [ -n "${PS1:-}" ] &&
   [ -z "${TERMOS_DASHBOARD_STARTED:-}" ] &&
   [ -x /usr/bin/python3 ] &&
   [ -f /opt/termos/dashboard.py ]; then
    export TERMOS_DASHBOARD_STARTED=1
    python3 /opt/termos/dashboard.py
fi
