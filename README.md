# home-network-monitoring
A lightweight home-network monitoring tool that tracks devices on your network by MAC address, records IP history, logs scan results over time, and calculates availability / uptime trends. The goal is to provide a clean dashboard-ready backend that’s safe, transparent, and ethical - only for networks you own or are authorized to monitor.

## How to use this project

### Setup your on your linux environment
- Find your subnet: 
  - ip addr | grep "inet"
    - you're looking for something that looks like 192.168.0.24/24 
    - your subnet would be 192.168.0.0/24, this is what you're scanning
- Only nmap -sn (host discovery only) is used to minimize intrusion and limit data collection to what is required. No port scanning or service enumeration is performed.
- Create the folder "Scans" on the desktop. This is where your scan files will be saved going forward
  - mkdir ~/Desktop/Scans

## Database Design
The relational schema is modeled using a MySQL Workbench EER (Entity–Relationship) Diagram, which defines the core entities (devices, device_ips, scan_runs, and device_scan_status) and their relationships. This design enforces referential integrity, supports historical IP tracking, and enables time-series availability analytics.