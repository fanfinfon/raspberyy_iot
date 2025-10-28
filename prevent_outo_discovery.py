import subprocess
import time

def run_cmd(cmd):
    """Run a shell command safely."""
    print(f"🔧 Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("⚠️ Error:", e.stderr.strip())

def harden_network(allowed_ips=None,new_hostname="raspberrypiw"):
    """
    Basic Raspberry Pi network hardening.
    - Hides from discovery
    - Allows only given IPs
    - Blocks everything else
    """
    print("\n Hardening Raspberry Pi Network ")
    if allowed_ips is None:
        allowed_ips = ["172.20.10.3"]  # default


    # 1. Change hostname 
    run_cmd(f"sudo hostnamectl set-hostname {new_hostname}")

    # 2. Disable Avahi (hides 'raspberrypi.local')
    run_cmd("sudo systemctl disable avahi-daemon")
    run_cmd("sudo systemctl stop avahi-daemon")

    # 3. Install and configure UFW firewall
    run_cmd("sudo apt install ufw -y")
    run_cmd("sudo ufw --force reset")
    run_cmd("sudo ufw default deny incoming")
    run_cmd("sudo ufw default allow outgoing")

    # 4. Allow only the trusted IPs
    for ip in allowed_ips:
        run_cmd(f"sudo ufw allow from {ip} to any port 1883 proto tcp")  # MQTT
        run_cmd(f"sudo ufw allow from {ip} to any port 22 proto tcp")    # SSH (optional)

    # 5. Enable UFW firewall
    run_cmd("sudo ufw --force enable")

    # 6. Disable a few unused/discoverable services
    for svc in ["cups", "vncserver-x11-serviced"]:
        run_cmd(f"sudo systemctl disable {svc}")
        run_cmd(f"sudo systemctl stop {svc}")

    print("🔒 Allowed IPs:", ", ".join(allowed_ips))

def restore_network(hostname="raspberrypiw"):
    """Revert network to normal."""
    print("\n Reverting Raspberry Pi Network To normal ")
    run_cmd("sudo hostnamectl set-hostname {hostname} ")
    run_cmd("sudo systemctl enable avahi-daemon")
    run_cmd("sudo systemctl start avahi-daemon")
    run_cmd("sudo ufw disable")

    for svc in ["cups", "vncserver-x11-serviced"]:
        run_cmd(f"sudo systemctl enable {svc}")
        run_cmd(f"sudo systemctl start {svc}")

    print("\n Network restored to normal state.")


