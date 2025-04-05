import os
import platform
import socket
import subprocess
import re


so = platform.system()
version = platform.release()





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


print(getMobuId(so))




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



# hostname = getHostname(so)

