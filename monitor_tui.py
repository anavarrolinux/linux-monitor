# Copyright (C) 2026 Anthony Navarro
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2.

#!/opt/linux-monitor/bin/python3

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.reactive import reactive
import sqlite3
import yaml
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
            "ui": {"refresh_interval": 60}
        }

config = load_config()

DB_PATH = config["database"]["path"]
REFRESH_INTERVAL = config["ui"]["refresh_interval"]

class LinuxServerMonitor(App):
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    CSS = """
    DataTable {
        height: 1fr;
        border: round $primary;
    }
            
    DataTable > .datatable--even-row {
        background: $primary 10%;
    }

    DataTable > .datatable--cursor {
        background: $accent 50%;
        color: $text;
        text-style: bold;
    }
    """

    CSS_PATH = None
    refresh_time = reactive(datetime.utcnow())

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        table = event.data_table
        table.sort(event.column_key, reverse=True)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield DataTable(id="host_table")
        yield Footer()

    def on_mount(self) -> None:
        table: DataTable = self.query_one("#host_table")
        table.zebra_striping = True
        table.cursor_type = "row"
        # Columns
        table.add_column("Hostname", width=25)
        table.add_column("IP", width=13)
        table.add_column("Status", width=6)
        table.add_column("OS", width=28)
        table.add_column("Kernel", width=28)
        table.add_column("CPU Load", width=8)
        table.add_column("Mem %", width=6)
        table.add_column("Disk %", width=6)
        table.add_column("Failed", width=6)
        table.add_column("Uptime", width=40)
        # Initial population
        table.focus()
        self.refresh_table()
        # Auto-refresh every REFRESH_INTERVAL seconds
        self.set_interval(REFRESH_INTERVAL, self.refresh_table)

    def refresh_table(self):
        table: DataTable = self.query_one("#host_table")
        table.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT hostname, ip_address, reachable, os_version, kernel_version,
                   cpu_load, cpu_cores, mem_used, disk_used, failed_services, uptime
            FROM hosts
            ORDER BY reachable DESC, hostname ASC
        """)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            hostname, ip, reachable, os, kernel, cpu, cpu_cores, mem, disk, failed, uptime = row

            # Color coding
            if reachable == 0:
                status_text = "[red]DOWN[/red]"
            else:
                status_text = "[green]UP[/green]"
            
            cpu_load = cpu if cpu is not None else 0.0
            core_count = cpu_cores if cpu_cores and cpu_cores > 0 else 1
            
            # Normalized load: 1.0 means 100% of all cores are busy
            saturation = cpu_load / core_count

            if saturation >= 1.0:
                # Highlighting because the CPU is "over-saturated"
                cpu_str = f"[bold red]{cpu_load:.2f}[/bold red]"
            elif saturation >= 0.7:
                # Warning because you're approaching the limit
                cpu_str = f"[yellow]{cpu_load:.2f}[/yellow]"
            else:
                cpu_str = f"{cpu_load:.2f}"

            mem_str = f"[bold red]{mem:.2f}[/bold red]" if mem is not None and mem >= 90 else (f"{mem:.2f}" if mem is not None else "-")
            disk_str = f"[bold red]{disk:.0f}[/bold red]" if disk is not None and disk >= 90 else (f"{disk:.0f}" if disk is not None else "-")
            failed_str = f"[bold red]{failed}[/bold red]" if failed is not None and failed > 0 else (str(failed) if failed is not None else "-")

            #cpu_str = f"{cpu:.2f}" if cpu is not None else "-"
            #mem_str = f"{mem:.2f}" if mem is not None else "-"
            #disk_str = f"{disk:.0f}" if disk is not None else "-"
            #failed_str = str(failed) if failed is not None else "-"

            table.add_row(
                hostname,
                ip or "-",
                status_text,
                os or "-",
                kernel or "-",
                cpu_str,
                mem_str,
                disk_str,
                failed_str,
                uptime or "-"
            )

def main():
    app = LinuxServerMonitor()
    app.run()

if __name__ == "__main__":
    main()
