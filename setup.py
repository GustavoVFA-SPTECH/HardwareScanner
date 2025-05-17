import os
import platform
import socket
import subprocess
import json
import re
import requests

API_BASE_URL = "http://44.208.193.41:3000/api"
HEADERS = {"Content-Type": "application/json"}

so = platform.system().lower()
version = platform.release()

def formatSize(bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f}"
        bytes /= 1024
    return f"{bytes:.2f}"


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
                    'size': formatSize(vol['Size'])
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
                        'size': int(formatSize(disk['size']))
                    })
        except Exception as e:
            print(f"Erro: {str(e)}")
    return disks_info


def getRam(so):
    try:
        if so == "windows":
            cmd = 'wmic memorychip get capacity'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                total_bytes = sum(int(num) for num in re.findall(r'\d+', result.stdout))
                return formatSize(total_bytes)

        elif so == "linux":
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                match = re.search(r'MemTotal:\s+(\d+)\s+kB', meminfo)
                if match:
                    return int(match.group(1)) * 1024
    except Exception as e:
        print(f"Erro ao obter RAM")


def getCpu(so):
    try:
        if so == "windows":
            command = 'wmic cpu get name'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                cpu_name = [line.strip() for line in result.stdout.split('\n') if line.strip()][1]
                return cpu_name

        elif so == "linux":
            command = "cat /proc/cpuinfo | grep 'model name' | uniq | cut -d ':' -f 2 | xargs"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()

    except Exception as e:
        print(f"Erro ao obter informações da CPU: {str(e)}")

    return "Informação não disponível"


def get_system_components(so):
    components = []

    disks = getDiscos(so)
    for disk in disks:
        components.append({
            'name': disk['path'],
            'type': 'Disk',
            'description': disk['size']
        })
    ram_size = getRam(so)
    components.append({
        'name': 'Memoria Ram',
        'type': 'Ram',
        'description': ram_size
    })

    cpu_name = getCpu(so)
    components.append({
        'name': cpu_name,
        'type': 'Cpu',
        'description': None
    })

    return components


def buscarUsuario(name, password):
    """Retorna (success, company_id, company_name) se válido"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={"name": name, "password": password},
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("Login realizado com sucesso!")
                return (True, data["company_id"], data["company_name"])
            else:
                print("Usuário ou senha incorretos!")
                return (False, None, None)
        else:
            print(f"Erro na requisição: {response.status_code}")
            return (False, None, None)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API: {e}")
        return (False, None, None)


def cadastrarMaquina(hostname, macAddress, mobuId, fkCompany):
    """Cadastra uma nova máquina e retorna o ID ou None em caso de erro"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/machines",
            json={
                "hostname": hostname,
                "macAddress": macAddress,
                "mobuId": mobuId,
                "fkCompany": fkCompany
            },
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("Máquina cadastrada com sucesso!")
                return data.get("machine_id")
            else:
                print(f"Erro ao cadastrar: {data.get('message')}")
        else:
            print(f"Erro na requisição: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API: {e}")

    return None


def buscarMaquina(mobuId, fkCompany):
    """Verifica se máquina existe e retorna seu ID ou None"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/machines",
            params={"mobuId": mobuId, "fkCompany": fkCompany},
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("exists"):
                return data["machine"]["idServer"]

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API: {e}")

    return None


def sync_components(fkServer, fkCompany, so):
    try:
        current_components = get_system_components(so)

        response = requests.post(
            f"{API_BASE_URL}/components/sync",
            json={
                "fkServer": fkServer,
                "fkCompany": fkCompany,
                "components": current_components
            },
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            print(data.get('message', 'Sincronização concluída com sucesso'))
            return True
        else:
            error_data = response.json()
            print(f"Erro na sincronização: {error_data.get('message', 'Erro desconhecido')}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com a API: {str(e)}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return False