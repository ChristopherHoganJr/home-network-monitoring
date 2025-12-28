# home-network-monitoring
A lightweight home-network monitoring tool that tracks devices on your network by MAC address, records IP history, logs scan results over time, and calculates availability / uptime trends. The goal is to provide a clean dashboard-ready backend that’s safe, transparent, and ethical - only for networks you own or are authorized to monitor.

## Database Design
The relational schema is modeled using a MySQL Workbench EER (Entity–Relationship) Diagram, which defines the core entities (devices, device_ips, scan_runs, and device_scan_status) and their relationships. This design enforces referential integrity, supports historical IP tracking, and enables time-series availability analytics.