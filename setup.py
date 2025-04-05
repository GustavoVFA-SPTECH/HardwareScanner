import os
import platform
import socket
import subprocess
import json
import re

so = platform.system().lower()
version = platform.release()


def formatSize(bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"

def getMobuId(so):
    try:
        if so == "windows":
            mobuId = subprocess.check_output(["powershell", "-Command",
                                                      "Get-WmiObject Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber"],
                                                     shell=True).decode().strip()
            if not mobuId:
                mobuId = "UUID não encontrado"
        elif so == "linux":
            mobuId = subprocess.check_output("sudo dmidecode -s system-uuid", shell=True).decode().strip()
        else:
            mobuId = "Desconhecido"
        return mobuId
    except Exception as e:
        print(f"Erro ao obter ID da placa-mãe: {str(e)}")
        return None

def getHostname(so):
    try:
        hostname = socket.gethostname()

        if so == 'linux' and not hostname:
            hostname = os.uname().nodename

        elif so == 'windows' and not hostname:
            hostname = os.popen('hostname').read().strip()

        return hostname

    except Exception as e:

        print(f"Erro ao obter hostname: {e}")
        return None

def getMacAddress(system):
    if system == "windows":
        try:
            output = subprocess.check_output(
                "getmac /v /FO list",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            )
            mac_match = re.search(r"([0-9A-F]{2}[:-]){5}([0-9A-F]{2})", output, re.IGNORECASE)
            if mac_match:
                return mac_match.group(0).upper()
        except:
            pass

    elif system == "linux":
        try:
            output = subprocess.check_output(
                "ip link show | grep 'link/ether' | head -n 1",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            )
            mac_match = re.search(r"([0-9a-f]{2}[:]){5}([0-9a-f]{2})", output.lower())
            if mac_match:
                return mac_match.group(0)
        except:
            try:
                output = subprocess.check_output(
                    "ifconfig | grep 'ether' | head -n 1",
                    shell=True,
                    text=True,
                    stderr=subprocess.DEVNULL
                )
                mac_match = re.search(r"([0-9a-f]{2}[:]){5}([0-9a-f]{2})", output.lower())
                if mac_match:
                    return mac_match.group(0)
            except:
                pass

    return None

def getDiscos(so):
    disks_info = []

    if so == "windows":
        try:
            command = "Get-Volume | Where-Object {$_.DriveLetter -ne $null} | Select-Object DriveLetter, Size | ConvertTo-Json"
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)

            volumes = json.loads(result.stdout)

            for vol in volumes:
                disks_info.append({
                    'path': f"{vol['DriveLetter']}:",
                    'size': vol['Size']
                })
        except Exception as e:
            print(f"Erro {str(e)}")

    elif so == "linux":
        try:
            command = "lsbdk -d -b -n -o NAME,SIZE --json"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            disks = json.loads(result.stdout)['blockdevices']

            for disk in disks:
                if disk['type'] == 'disk':
                    disks_info.append({
                        'path': f"/dev/{disk['name']}",
                        'size': int(disk['size'])
                    })
        except Exception as e:
            print(f"Erro: {str(e)}")
    print(disks_info)
    return disks_info

def getRam(so):
    try:
        if so == "windows":
            cmd = 'wmic memorychip get capacity'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                total_bytes = sum(int(num) for num in re.findall(r'\d+', result.stdout))
                return total_bytes

        elif so == "linux":
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                match = re.search(r'MemTotal:\s+(\d+)\s+kB', meminfo)
                if match:
                    return int(match.group(1)) * 1024
    except Exception as e:
        print(f"Erro ao obter RAM")

def getCpu():
    return

