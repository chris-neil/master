import argparse
import getpass
import json
import logging
import sys
from typing import Optional
import requests
import paramiko

#!/usr/bin/env python3
"""
Linearized version of the original change_backup_server.py script.

All functionality is in a single top-to-bottom block (no function definitions).
Behavior preserved: login to management API, list gateways, extract IPs, SSH to each
gateway and run the provided command template.
"""


# Basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


parser = argparse.ArgumentParser(description="Change Gaia backup server IP on all gateways via Management API + SSH")
parser.add_argument("--mgmt-host", required=True, help="Management server hostname or IP (web_api)")
parser.add_argument("--mgmt-user", required=True, help="Management API username")
parser.add_argument("--mgmt-pass", help="Management API password (if omitted, prompt)")
parser.add_argument("--new-backup", required=True, help="New Gaia backup server IP address to set")
parser.add_argument("--ssh-user", required=True, help="SSH username for gateways")
parser.add_argument("--ssh-pass", help="SSH password for gateways (omit to prompt). If using key, omit password.")
parser.add_argument("--ssh-key", help="Path to private key for SSH auth (optional)")
parser.add_argument(
    "--cmd-template",
    default='clish -c "set backup-server {ip}"',
    help='Command template to run on gateway with {ip} placeholder for new backup IP '
    "(default: 'clish -c \"set backup-server {ip}\"')",
)
parser.add_argument("--dry-run", action="store_true", help="Don't perform SSH commands, just print targets and commands")
parser.add_argument("--use-gateway-api", action="store_true", help="Use HTTP(S) API on each gateway instead of SSH")
parser.add_argument("--gw-api-url-template", help="Gateway API URL template containing {ip} and/or {name}, e.g. 'https://{ip}/api/cli'")
parser.add_argument(
    "--gw-api-payload-template",
    default='{"command": "{cmd}"}',
    help='JSON payload template for gateway API with {cmd}/{ip}/{name} placeholders (default: "{\"command\": \"{cmd}\"}")',
)
parser.add_argument("--gw-api-user", help="HTTP basic auth user for gateway API (optional)")
parser.add_argument("--gw-api-pass", help="HTTP basic auth password for gateway API (omit to prompt)")
parser.add_argument("--gw-api-token", help="Bearer token for gateway API (mutually exclusive with user/pass)")
parser.add_argument("--gw-api-verify", action="store_true", help="Verify TLS certificates when connecting to gateway APIs (default: not verified)")
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()

if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

mgmt_pass = args.mgmt_pass or getpass.getpass("Management API password: ")
ssh_pass = args.ssh_pass
if not ssh_pass and not args.ssh_key:
    ssh_pass = getpass.getpass("Gateway SSH password: ")

# Prompt for gateway API password if needed
gw_api_pass = args.gw_api_pass
if args.use_gateway_api and args.gw_api_user and not gw_api_pass and not args.gw_api_token:
    gw_api_pass = getpass.getpass("Gateway API password: ")

session = requests.Session()
# disable warnings for self-signed certs often used in labs; in production supply proper cert validation.
requests.packages.urllib3.disable_warnings()

# --- login to management API (inlined) ---
try:
    login_url = f"https://{args.mgmt_host}/web_api/login"
    resp = session.post(login_url, json={"user": args.mgmt_user, "password": mgmt_pass}, verify=False, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    sid = data.get("sid")
    if not sid:
        logging.error("Login succeeded but no SID returned")
        sys.exit(1)
    session.cookies.set("X-chkp-sid", sid)
    logging.debug("Management API login successful, SID set")
except Exception as e:
    logging.error("Failed to login to management API: %s", e)
    sys.exit(1)

try:
    # --- get gateways (inlined) ---
    gw_url = f"https://{args.mgmt_host}/web_api/show-gateways-and-servers"
    payload = {"details-level": "full"}
    resp = session.post(gw_url, json=payload, verify=False, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    objects = data.get("objects") or []
    logging.info("Found %d gateway/server objects", len(objects))

    # build target list (inlined extract_ip logic)
    targets = []
    for obj in objects:
        typ = obj.get("type", "").lower()
        if "gateway" in typ or "server" in typ:
            # try several common fields for an IP
            ip = None
            for key in ("ipv4-address", "ip-address", "management-ip"):
                v = obj.get(key)
                if v:
                    ip = v
                    break
            if not ip and "interfaces" in obj:
                for iface in obj.get("interfaces", []):
                    if iface.get("ipv4-address"):
                        ip = iface.get("ipv4-address")
                        break

            name = obj.get("name", "<unnamed>")
            if ip:
                targets.append({"name": name, "ip": ip})
            else:
                logging.warning("Skipping %s (no IP found)", name)

    logging.info("Prepared %d targets to update", len(targets))

    # iterate targets and run SSH commands (inlined ssh_run_command)
    for t in targets:
        cmd = args.cmd_template.format(ip=args.new_backup)
        logging.info("Target %s (%s): command: %s", t["name"], t["ip"], cmd)
        if args.dry_run:
            continue

        # If requested, use gateway HTTP API instead of SSH
        if args.use_gateway_api:
            if not args.gw_api_url_template:
                logging.error("--use-gateway-api requires --gw-api-url-template")
                continue

            url = args.gw_api_url_template.format(ip=t["ip"], name=t["name"])
            payload_str = args.gw_api_payload_template.format(cmd=cmd, ip=t["ip"], name=t["name"])
            headers = {}
            auth = None
            if args.gw_api_token:
                headers["Authorization"] = f"Bearer {args.gw_api_token}"
            elif args.gw_api_user:
                auth = (args.gw_api_user, gw_api_pass)

            verify = args.gw_api_verify
            logging.info("Calling gateway API %s", url)
            if args.dry_run:
                logging.debug("Dry-run payload: %s", payload_str)
                continue

            try:
                # try to send JSON if payload_str is JSON, otherwise send as raw data
                try:
                    payload_obj = json.loads(payload_str)
                    resp = requests.post(url, json=payload_obj, headers=headers or None, auth=auth, verify=verify, timeout=30)
                except ValueError:
                    resp = requests.post(url, data=payload_str, headers=headers or None, auth=auth, verify=verify, timeout=30)

                resp.raise_for_status()
                logging.info("Gateway API call succeeded for %s", t["ip"])
                logging.debug("Response: %s", resp.text)
            except Exception as e:
                logging.error("Gateway API call failed for %s: %s", t["ip"], e)

        else:
            logging.info("Connecting to %s as %s", t["ip"], args.ssh_user)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                if args.ssh_key:
                    key = paramiko.RSAKey.from_private_key_file(args.ssh_key)
                    client.connect(hostname=t["ip"], username=args.ssh_user, pkey=key, timeout=30)
                else:
                    client.connect(hostname=t["ip"], username=args.ssh_user, password=ssh_pass, timeout=30)

                stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
                out = stdout.read().decode(errors="ignore")
                err = stderr.read().decode(errors="ignore")
                rc = stdout.channel.recv_exit_status()
                logging.info("Command on %s finished rc=%s", t["ip"], rc)
                if out:
                    logging.debug("STDOUT: %s", out.strip())
                if err:
                    logging.debug("STDERR: %s", err.strip())

                if rc != 0:
                    logging.error("Command failed on %s (rc=%s). stderr: %s", t["ip"], rc, err.strip())
                else:
                    logging.info("Command succeeded on %s", t["ip"])

            except Exception as e:
                logging.error("SSH command failed on %s: %s", t["ip"], e)
            finally:
                try:
                    client.close()
                except Exception:
                    pass

finally:
    # logout (inlined)
    try:
        logout_url = f"https://{args.mgmt_host}/web_api/logout"
        session.post(logout_url, json={}, verify=False, timeout=10)
    except Exception:
        pass
