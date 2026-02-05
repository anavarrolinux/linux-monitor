## Linux Infrastructure Monitor (TUI)

A high-performance, concurrent monitoring tool designed for Rocky Linux 9 environments. It uses a Python-based collector to gather system metrics via SSH and displays them in a real-time Terminal User Interface (TUI).

🛠 Features

 - Asynchronous Collection: Uses ThreadPoolExecutor to poll multiple Rocky Linux 9 nodes simultaneously, ensuring the monitoring scale doesn't lag with more hosts.
 - Modern TUI: Built with the Textual framework for a responsive, interactive dashboard.
 - Database Concurrency: Leverages SQLite with Write-Ahead Logging (WAL) mode, allowing the TUI to read data without being blocked by the collector's write operations.
 - Systemd Integration: Designed to run as a secured native Linux daemon using systemd services and timers for "set and forget" reliability.
 - Security First: Uses paramiko for SSH communication, utilizing system host keys and rejecting unknown hosts to maintain a secure environment.

🏗 Architecture

The system is split into three main components:

- `collect.py`: The backend engine that parses /proc and os-release data from remote nodes.
- `config.yaml`: A centralized configuration file for managing SSH users, database paths, and polling intervals.
- `monitor_tui.py`: The frontend dashboard providing real-time visibility into CPU load, memory saturation, and failed systemd services.

Security Model
- Host key policy: Rejects unknown hosts
- Least privilege: Recommend a dedicated user with minimal sudo (or no sudo)
- Command surface area: It is a fixed command block for ease of use and consistant reporting
- Data sensitivity: Only Hostname, IP, Pretty OS Name, Kernel version, Resources (CPU Load, MEM%, / Disk% and Uptime) are stored in SQLite and retention possible by backing up the .db file
- Operational mode: collector can be automated via systemd service + timer (Examples Included)

🚀 Deployment (Rocky Linux 9)
Prerequisites

    Python 3.9+

Pre-Linux-Monitor Preparation

    vim /etc/hosts (eg. x.x.x.x <Server-Hostname>)
    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 <Server-Hostname>
    ssh-copy-id -i ~/.ssh/id_ed25519 <Server-Hostname>
    ssh <Server-Hostname> #Verify that passwordless SSH is setup Correctly 
    Setup Users, Create /etc/sudoers.d/<User> if required

Linux-Monitor Installation

    sudo git clone https://github.com/anavarrolinux/linux-monitor.git /opt/linux-monitor
    sudo python3 -m venv /opt/linux-monitor
    cd /opt/linux-monitor
    source bin/activate
    sudo chown <User>:<User>-R /opt/linux-monitor
    sudo chmod 700 -R /opt/linux-monitor
    pip install .

Linux Monitor TUI
<img width="1593" height="808" alt="LinuxMonitorTUI" src="https://github.com/user-attachments/assets/2df8d018-2be3-4f30-b9c9-1a9c162a04d9" />

Initial scaffolding was AI-assisted; functionality, testing, debugging, and final design decisions were implemented through iterative development and validation.
