import subprocess
import re
import json

class SystemDiscoverer:
    """Scans active listening sockets and services on Linux/WSL2."""

    def scan_sockets(self):
        sockets = []
        try:
            # Added 'sudo' so Linux exposes process names attached to ports
            res = subprocess.run(["sudo", "ss", "-tulpn"], capture_output=True, text=True)
            lines = res.stdout.strip().split("\n")[1:]

            for line in lines:
                parts = re.split(r'\s+', line)
                if len(parts) >= 5:
                    port = parts[4].split(":")[-1]
                    proc_match = re.search(r'users:\(\("([^"]+)"', line)
                    process = proc_match.group(1) if proc_match else "unknown"
                    sockets.append({"port": port, "process": process})
        except Exception as e:
            print(f"[Warning] Socket scan failed: {e}")
        return sockets
    
    def scan_services(self):
        services = {}
        for svc in ["nginx", "ssh"]:
            try:
                res = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
                services[svc] = {
                    "status": res.stdout.strip() or "inactive",
                    "config_path": f"/etc/{svc}/nginx.conf" if svc == "nginx" else "/etc/ssh/sshd_config"
                }
            except Exception:
                services[svc] = {"status": "unknown"}
        return services

if __name__ == "__main__":
    sd = SystemDiscoverer()
    output = {
        "services": sd.scan_services(),
        "sockets": sd.scan_sockets()
    }
    print(json.dumps(output, indent=2))