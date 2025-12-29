import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import logging

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error as MySQLError

# Logging setup
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s [%(levelname)s] %(message)s',
)

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', "localhost"),
    'user': os.getenv('DB_USER', "root"),
    'password': os.getenv('DB_PASSWORD', ""),
    'database': os.getenv('DB_NAME', "home_network_monitor")
}

db_port = os.getenv('DB_PORT')
if db_port:
    try:
        DB_CONFIG['port'] = int(db_port)
    except ValueError:
        logger.warning(
            f"Invalid DB_PORT value: {db_port}. Using default MYSQL port.")

SUBNET = os.getenv('SUBNET', '192.168.0.0/24')
NMAP_PATH = os.getenv('NMAP_PATH', '/usr/bin/nmap')


def get_db_connection():
    # Create and return a new MySQL connection using DB_CONFIG
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except MySQLError as e:
        logger.error(f"Error connecting to MySQL DB: {e}")
        raise


# NMAP helpers

def run_nmap_scan():
    # Using -PR for ARP-based discovery instead of ICMP ping (ARP cannot be blocked like ICMP)
    cmd = ["sudo", NMAP_PATH, "-sn", "-PR", SUBNET, "-oX", "-"]
    logger.info(f'Running nmap scan: {" ".join(cmd)}')

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f'nmap scan failed: {e}')
        logger.error(f'nmap stderr: {e.stderr}')
        raise


def parse_nmap_xml(xml_str):
    """
    Parse nmap XML and yield dicts like:
    {
        "mac_address": str or None,
        "ip_address": str or None,
        "hostname": str or None,
        "vendor": str or None,
        "status": "up" or "down" or "unknown"
    }
    """
    root = ET.fromstring(xml_str)

    for host in root.findall('host'):
        status_el = host.find('status')
        status = status_el.get('state') if status_el is not None else 'unknown'

        ip = None
        mac = None
        vendor = None

        for addr in host.findall('address'):
            addr_type = addr.get('addrtype')
            if addr_type == 'ipv4':
                ip = addr.get('addr')
            elif addr_type == 'mac':
                mac = addr.get('addr')
                vendor = addr.get('vendor')

        hostname_el = host.find('hostnames/hostname')
        hostname = hostname_el.get('name') if hostname_el is not None else None

        yield {
            "mac_address": mac,
            "ip_address": ip,
            "hostname": hostname,
            "vendor": vendor,
            "status": status
        }


# DB Write Helpers
def utc_now():
    # Return a timezone-aware UTC datetime
    return datetime.now(timezone.utc)


def insert_scan_run_start(cursor):
    # Insert a new row into scan_runs and return the scan_id
    now = utc_now()
    sql = """
        INSERT INTO scan_runs (started_at, finished_at, total_hosts, up_hosts, notes)
        VALUES (%s, NULL, 0, 0, %s)
    """
    cursor.execute(sql, (now, "automated scan"))
    scan_id = cursor.lastrowid
    logger.info(f'Inserted new scan_run with id {scan_id}')
    return scan_id


def update_scan_run_end(cursor, scan_id, total_hosts, up_hosts):
    # Update the scan_runs row with final counts at finished_at
    sql = """
        UPDATE scan_runs
        SET finished_at = %s,
            total_hosts = %s,
            up_hosts = %s
        WHERE scan_id = %s
    """
    cursor.execute(sql, (utc_now(), total_hosts, up_hosts, scan_id))
    logger.info(
        f'Updated scan_run {scan_id} with total_hosts={total_hosts}, up_hosts={up_hosts}'
    )


def upsert_device(cursor, host):
    """
    Insert or update row in devices.
    Uses Mac_address as the PK
    """
    mac = host['mac_address']
    if mac is None:
        # Rare edge case: host without MAC address
        logger.debug("Host without MAC address skipped.")
        return

    hostname = host['hostname']
    vendor = host['vendor']
    status = host['status']
    is_up = 1 if status == 'up' else 0
    now = utc_now()

    sql = """
        INSERT INTO devices (
            mac_address, first_seen, last_seen, hostname, vendor, total_scans, up_scans, last_status
        ) VALUES (
            %s, %s, %s, %s, %s, 1, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            last_seen = VALUES(last_seen),
            hostname = COALESCE(VALUES(hostname), hostname),
            vendor = COALESCE(VALUES(vendor), vendor),
            total_scans = total_scans + 1,
            up_scans = up_scans + VALUES(up_scans),
            last_status = VALUES(last_status)
    """

    cursor.execute(
        sql,
        (
            mac,
            now,
            now,
            hostname,
            vendor,
            is_up,  # up_scans for new row
            is_up  # last_status (0 or 1)
        )
    )


def upsert_device_ip(cursor, host):
    """
    Upsert IP history for a device in device_ips table

    - clear existing is_current flags for that MAC address
    - insert/update the (mac, ip) pair with last_seen and times_seen
    """
    mac = host['mac_address']
    ip = host['ip_address']
    if mac is None or ip is None:
        return

    now = utc_now()

    # Clear existing 'current' flags for this MAC
    cursor.execute(
        'UPDATE device_ips SET is_current = 0 WHERE mac_address = %s', (mac,),
    )

    sql = """
        INSERT INTO device_ips (
            mac_address, ip_address, first_seen, last_seen, is_current, times_seen
        ) VALUES (
            %s, %s, %s, %s, 1, 1
        )
        ON DUPLICATE KEY UPDATE
            last_seen = VALUES(last_seen),
            times_seen = times_seen + 1,
            is_current = 1
    """

    cursor.execute(sql, (mac, ip, now, now))


def insert_device_scan_status(cursor, scan_id, host):
    """
    Insert a row into device_scan_status for this scan and device
    """
    mac = host['mac_address']
    if mac is None:
        return

    status = 1 if host['status'] == 'up' else 0

    sql = """
        INSERT INTO device_scan_status (
            status, mac_address, scan_id
        ) VALUES (
            %s, %s, %s
        )
    """
    cursor.execute(sql, (status, mac, scan_id))


# Main scanner logic
def main():
    logger.info('Starting network scan run')

    try:
        xml_str = run_nmap_scan()
    except Exception:
        logger.exception('Nmap scan failed, aborting.')
        return

    try:
        hosts = list(parse_nmap_xml(xml_str))
    except Exception:
        logger.exception('Failed to parse nmap XML output, aborting.')
        return

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        scan_id = insert_scan_run_start(cursor)

        total_hosts = 0
        up_hosts = 0

        for host in hosts:
            mac = host.get('mac_address')
            if not mac:
                # debugging log for hosts without MAC
                logger.debug(
                    f'Skipping host without MAC: {host}'
                )
                continue

            total_hosts += 1
            if host['status'] == 'up':
                up_hosts += 1

            upsert_device(cursor, host)
            upsert_device_ip(cursor, host)
            insert_device_scan_status(cursor, scan_id, host)

        update_scan_run_end(cursor, scan_id, total_hosts, up_hosts)
        conn.commit()
        logger.info('Scan run committed successfully.')

    except MySQLError:
        logger.exception(
            'MySQL error during scan processing; rolling back transaction.')
        if conn is not None:
            conn.rollback()
    except Exception:
        logger.exception('Unexpected error during scan processing.')
        if conn is not None:
            conn.rollback()
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            logger.info('Database connection closed.')


logger.info('Network scan run completed.')

if __name__ == '__main__':
    main()
