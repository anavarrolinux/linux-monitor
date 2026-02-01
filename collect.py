# Copyright (C) 2026 Anthony Navarro
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2.

#!/opt/linux-monitor/bin/python3

import paramiko
import sqlite3
import socket
import yaml
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

def load_config(config_path="/opt/linux-monitor/config.yaml"):
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return defaults if config fails
        return {
            "database": {"path": "/opt/linux-monitor/monitor.db"},
            "ssh": {"user": "anavarro", "timeout": 5, "max_workers": 10},
            "files": {"servers_list": "/opt/linux-monitor/servers.txt"},
            "ui": {"refresh_interval": 60}
        }

config = load_config()

# ---------------- CONFIG ----------------
DB_PATH = config["database"]["path"]
SSH_USER = config["ssh"]["user"]
SERVERS_FILE = config["files"]["servers_list"]
MAX_WORKERS = config["ssh"].get("max_workers", 10)
SSH_TIMEOUT = config["ssh"].get("timeout", 5)

COMMAND = r"""
echo LOAD $(awk '{print $1}' /proc/loadavg)
echo CORES $(nproc)
echo MEM $(free | awk '/Mem:/ {printf "%.2f", $3/$2*100}')
echo DISK $(df / | awk 'END {print $5}' | tr -d '%')
echo UPTIME $(uptime -p)
echo FAILED $(systemctl --failed --no-legend | wc -l)
echo KERNEL $(uname -r)
echo OS $(. /etc/os-release && echo "$PRETTY_NAME")
"""

# ----------------------------------------

def load_servers():
    return [
        line.strip()
        for line in Path(SERVERS_FILE).read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

def resolve_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        return None


def ssh_collect(hostname):
    now = datetime.utcnow().isoformat(timespec="seconds")
    ip = resolve_ip(hostname)

    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        ssh.connect(
            hostname=hostname,
            username=config['ssh']['user'],
            timeout=config['ssh']['timeout'],
        )

        _, stdout, _ = ssh.exec_command(COMMAND)
        output = stdout.read().decode()
        ssh.close()

        data = {}
        for line in output.splitlines():
            key, value = line.split(" ", 1)
            data[key] = value.strip()

        return {
            "hostname": hostname,
            "ip": ip,
            "reachable": 1,
            "cpu": float(data["LOAD"]),
            "cores": float(data["CORES"]),
            "mem": float(data["MEM"]),
            "disk": float(data["DISK"]),
            "uptime": data["UPTIME"],
            "failed": int(data["FAILED"]),
            "kernel": data["KERNEL"],
            "os": data["OS"],
            "last_seen": now,
            "last_checked": now,
        }

    except Exception as e:
        print(f"[UNREACHABLE] {hostname}: {e}")
        return {
            "hostname": hostname,
            "ip": ip,
            "reachable": 0,
            "last_checked": now,
        }

def main():
    servers = load_servers()
    db_file = Path(DB_PATH)
    db_file.parent.mkdir(parents=True, exist_ok=True) # Ensure /opt/linux-monitor exists
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    
    # Auto-create hosts table if it doesn't exist
    conn.execute("""
    CREATE TABLE IF NOT EXISTS hosts (
        hostname TEXT PRIMARY KEY,
        ip_address TEXT,
        os_version TEXT,
        kernel_version TEXT,
        cpu_load REAL,
        cpu_cores REAL,
        mem_used REAL,
        disk_used REAL,
        uptime TEXT,
        failed_services INTEGER,
        reachable INTEGER DEFAULT 0,
        last_checked DATETIME,
        last_seen DATETIME,
        first_seen DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for result in pool.map(ssh_collect, servers):
            conn.execute("""
                INSERT INTO hosts (
                    hostname, ip_address, os_version, kernel_version,
                    cpu_load, cpu_cores, mem_used, disk_used, uptime,
                    failed_services, reachable,
                    last_checked, last_seen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(hostname)
                DO UPDATE SET
                    ip_address       = excluded.ip_address,
                    os_version       = COALESCE(excluded.os_version, hosts.os_version),
                    kernel_version   = COALESCE(excluded.kernel_version, hosts.kernel_version),
                    cpu_load         = excluded.cpu_load,
                    cpu_cores        = excluded.cpu_cores,
                    mem_used         = excluded.mem_used,
                    disk_used        = excluded.disk_used,
                    uptime           = excluded.uptime,
                    failed_services  = excluded.failed_services,
                    reachable        = excluded.reachable,
                    last_checked     = excluded.last_checked,
                    last_seen        = COALESCE(excluded.last_seen, hosts.last_seen)
           """ , (
                result ["hostname"],
                result.get("ip"),
                result.get("os"),
                result.get("kernel"),
                result.get("cpu"),
                result.get("cores"),
                result.get("mem"),
                result.get("disk"),
                result.get("uptime"),
                result.get("failed"),
                result["reachable"],
                result["last_checked"],         
                result.get("last_seen"),
             ))
      
    conn.commit()
    conn.close()

    print(f"[{datetime.utcnow()}] Poll completed for {len(servers)} hosts")

if __name__ == "__main__":
    main()
