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
        if so == 'windows':
            command = 'wmic baseboard get serialnumber /value'
            result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
            match = re.search(r'SerialNumber=([^\r\n]+)', result)
            if match:
                serial = match.group(1).strip()
                if serial and serial.lower() not in ['na', 'none', 'to be filled of by o.e.m', 'empty']:
                    return serial
            return None

        elif so == 'linux':
            try:
                with open('/sys/class/dmi/id/board_serial', 'r') as f:
                    return f.read().strip()
            except:
                command = 'sudo dmicode -s baseboard-serial-number'
                result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
                return result.strip() if result.strip() else None
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
    return disks_info

getDiscos(so)


def getRam():
    return

def getCpu():
    return
