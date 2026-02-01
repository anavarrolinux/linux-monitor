## Linux Infrastructure Monitor (TUI)

A high-performance, concurrent monitoring tool designed for Rocky Linux 9 environments. It uses a Python-based collector to gather system metrics via SSH and displays them in a real-time Terminal User Interface (TUI).

🛠 Features
    
    Asynchronous Collection: Uses ThreadPoolExecutor to poll multiple Rocky Linux 9 nodes simultaneously, ensuring the monitoring scale doesn't lag with more hosts.
    
    Modern TUI: Built with the Textual framework for a responsive, interactive dashboard.
    
    Database Concurrency: Leverages SQLite with Write-Ahead Logging (WAL) mode, allowing the TUI to read data without being blocked by the collector's write operations.
    
    Systemd Integration: Designed to run as a native Linux daemon using systemd services and timers for "set and forget" reliability.
    
    Security First: Uses paramiko for SSH communication, utilizing system host keys and rejecting unknown hosts to maintain a secure environment.

🏗 Architecture

The system is split into three main components:
    
    collect.py: The backend engine that parses /proc and os-release data from remote nodes.
    
    config.yaml: A centralized configuration file for managing SSH users, database paths, and polling intervals.
    
    monitor_tui.py: The frontend dashboard providing real-time visibility into CPU load, memory saturation, and failed systemd services.

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

    git clone https://github.com/anavarrolinux/linux-monitor.git /opt/linux-monitor
    cd /opt/linux-monitor
    python3 -m venv venv
    source venv/bin/activate
    pip install .

Linux Monitor TUI
<img width="1593" height="608" alt="image" src="https://github.com/user-attachments/assets/2df8d018-2be3-4f30-b9c9-1a9c162a04d9" />

    
