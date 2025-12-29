# 🏠 Home Network Monitoring (Python + Nmap + MySQL)

A lightweight home-network monitoring tool that tracks devices by **MAC address**, records **IP history over time**, logs **scan sessions**, and enables **availability / uptime analytics** - with ethics and privacy built-in.

The project is designed to be:

✔ Transparent - host discovery only (`nmap -sn`)  
✔ Safe - tracks devices you own or are authorized to monitor  
✔ Dashboard-ready - clean relational schema + backend scanner  
✔ Resume-quality - real engineering design, not a toy script

I built this to grow stronger in **Python, networking, MySQL, security, and full-stack engineering** - while building something actually useful in my home lab.

---

## ⚠️ Ethics & Responsible Use

> **Only scan networks you own or are explicitly authorized to monitor.**  
> This tool intentionally uses **host discovery only (`nmap -sn`)** - meaning:  
> ❌ No port scanning  
> ❌ No service enumeration  
> ❌ No exploitation

This project exists to help understand your own network, improve security awareness, and learn real-world engineering - **not hacking**.

---

## ✨ Features

- 🔍 Detect devices on your network by **MAC address**
- 🏷 Add **friendly names, labels & locations**
- 📜 Track **IP address history over time**
- 📊 Record **scan sessions for trend analysis**
- 🟢 Enable **availability tracking & uptime metrics**
- ⚙️ Clean separation of scanner + database logic
- 🌱 Future-proofed for a **Next.js dashboard (WIP)**

---

## 🧠 High-Level Architecture

Linux VM (Python Scanner + nmap)
⬇
MySQL Database (Windows or any host)
⬇
Dashboard UI (Next.js)

The scanner runs on a Linux machine, the database can live anywhere (mine runs on a Windows laptop), and the dashboard reads from the DB.

This creates a real **distributed system** - even at home 💪

---

## 🗄 Database Design

The database is modeled using a **MySQL Workbench EER diagram**, enforcing referential integrity and supporting historical + time-series data.

### Core Tables

| Table                | Purpose                                      |
| -------------------- | -------------------------------------------- |
| `devices`            | One row per MAC address (canonical identity) |
| `device_ips`         | Tracks every IP a device has ever used       |
| `scan_runs`          | One row per scan execution session           |
| `device_scan_status` | Per-device status recorded for each scan     |

### Design Highlights

- MAC address = **source-of-truth identity**
- Tracks **current + historical IPs**
- Tracks **up/down status per scan**
- Enables **availability analytics**
- Uses **foreign keys + cascading deletes**

This is not throwaway logging - it’s **structured network telemetry**.

---

## 🧩 Tech Stack

### Scanner

- Python 3
- `nmap` (host discovery only)
- `python-dotenv`
- `mysql-connector-python`

### Database

- MySQL 8+
- MySQL Workbench (EER modeling)

### Dashboard (WIP)

- Next.js (App Router)
- TailwindCSS
- mysql2

---

## 🛠 Requirements

- Linux machine or VM to run the scanner
- MySQL database server
- Python 3.10+
- `nmap`

---

## 🔐 Environment Variables

Copy `.env.example` → `.env` and configure:

```env
# Database
DB_HOST=192.168.0.10
DB_PORT=3306
DB_USER=USERNAME
DB_PASSWORD=CHANGE_ME
DB_NAME=home_network_monitor
```

# Network scanning

SUBNET=192.168.0.0/24
SCAN_OUTPUT_DIR=/home/youruser/Desktop/Scans

# Logging

LOG_LEVEL=INFO

.env is git-ignored - never commit real credentials.

---

## 📦 Install Python Dependencies

`pip install -r requirements.txt`

(or manually)

`pip install mysql-connector-python python-dotenv`

---

## 🌐 Find Your Subnet (Linux)

`ip addr | grep inet`

Example output:

192.168.0.24/24

So your subnet is:

192.168.0.0/24

---

## 📁 Create Scan Output Directory

`mkdir ~/Desktop/Scans`

---

## 🛰 About Network Scanning Mode

This project uses **host discovery only**:

`nmap -sn <subnet>`

This means:

- ✔ Detects whether hosts exist
- ❌ Does not port scan
- ❌ Does not fingerprint services

This keeps the tool **non-intrusive and ethical**.

---

## ▶️ Running the Scanner

python scanner.py

The scanner will:

1. Run nmap -sn
2. Parse discovered hosts
3. Insert or update device records
4. Log scan-session metadata
5. Track availability & history over time

---

## 🔁 Optional: Automate with Cron

Example - run every 10 minutes

`*/10 * * * * /usr/bin/python3 /path/to/scanner.py >> /var/log/netmon.log 2>&1`

---

## 📊 Dashboard (Next.js - In Progress)

Planned UI features include:

- Device list with status indicator
- Friendly names & hostnames
- Vendor & device type info
- IP history timeline
- Availability % charts
- Filters (critical / ignored / offline)
- Location tagging (room / area)
- Device detail pages

This README will be updated as the UI ships 🚀

---

## 🧪 Why I Built This

I wanted a project that:

- Blends **Python + Networking + SQL**
- Uses **real-world data (my network)**
- Follows **ethical boundaries**
- Demonstrates **database design**
- Runs across **multiple machines**
- Builds toward a **production-style stack**

This repo is part of my journey toward becoming a stronger:

\*\*Software Engineer · DevOps Engineer · Security-minded Builder

And honestly - I'm having fun doing it 😄

---

## 🛡 Security Considerations

This project uses:

- **Least-privilege DB users (not root)**
- Host-restricted DB accounts (user@ip)
- Network-restricted DB ports
- .env for secrets (git-ignored)
- Non-intrusive host discovery mode

Future enhancements may include:

- TLS DB connections
- Optional dashboard authentication
- Encrypted backups

---

## 📌 Roadmap

- [x] Design relational schema
- [x] Build scanner + DB ingestion
- [x] Secure remote DB connectivity
- [ ] Next.js dashboard MVP
- [ ] Availability % charts
- [ ] Device detail pages
- [ ] Export / backup support
- [ ] Docker Compose setup (scanner + DB + UI)

---

## 🤝 Contributions

Right now this is a learning + personal project, but constructive feedback is always welcome.

---

## 📜 License

MIT - use, learn, and improve responsibly.

---

## ❤️ Acknowledgements

Built after too many cups of coffee, lots of debugging, and a stubborn desire to understand my own network from the inside out 😅
