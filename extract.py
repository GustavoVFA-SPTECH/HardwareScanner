import psutil

def cpuData():
    cpuFreq = psutil.cpu_freq()
    cpuPercent = psutil.cpu_percent()
    
    return cpuFreq, cpuPercent

def ramData():
    ramUsed = psutil.virtual_memory().used
    ramPercent = psutil.virtual_memory().percent
    
    return ramUsed, ramPercent

def diskData(path):
    diskUsed = psutil.disk_usage(path).used
    diskPercent = psutil.disk_usage(path).percent

    return diskUsed, diskPercent

def processData():
    for proc in psutil.process_iter([]):
        print(proc.name())
        print(proc.memory_percent())
        print(proc.cpu_percent())
        print(proc.memory_info().vms)

import csv
from datetime import datetime
import time

from setup import getDiscos, so, getMobuId

def monitor_system(companyName, mobuID):
    record_count = 0
    current_file = None
    discos = None

    def create_new_file():
        nonlocal current_file, discos, record_count
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{companyName}_{mobuID}_{timestamp}.csv"

        discos = getDiscos(so)
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            headers = ['data_hora', 'cpu_freq', 'cpu_percent', 'ram_used', 'ram_percent']

            for disco in discos:
                path_safe = disco['path'].replace('/', '_').replace('\\', '_').replace(':', '')
                headers.extend([
                    f'disco_{path_safe}_used',
                    f'disco_{path_safe}_percent'
                ])

            writer.writerow(headers)

        print(f"Novo arquivo de monitoramento criado: {output_file}")
        record_count = 0
        return output_file, discos

    current_file, discos = create_new_file()

    while True:
        try:
            if record_count >= 100:
                current_file, discos = create_new_file()

            data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            cpuFreq, cpuPercent = cpuData()
            ramUsed, ramPercent = ramData()

            row = [
                data_hora,
                cpuFreq.current,
                cpuPercent,
                ramUsed,
                ramPercent
            ]

            for disco in discos:
                try:
                    disk_used, disk_percent = diskData(disco['path'])
                    row.extend([disk_used, disk_percent])  # Removido o path da linha
                except Exception as e:
                    print(f"Erro ao acessar disco {disco['path']}: {str(e)}")
                    row.extend([None, None])  # Mantém None para os valores de erro

            with open(current_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

            record_count += 1
            time.sleep(2)

        except KeyboardInterrupt:
            print("\nMonitoramento encerrado pelo usuário")
            break
        except Exception as e:
            print(f"Erro durante o monitoramento: {str(e)}")
            time.sleep(2)

monitor_system('teste', getMobuId(so))