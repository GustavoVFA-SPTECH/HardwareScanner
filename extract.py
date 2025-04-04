import psutil



# Extração dados da CPU

def cpuData():
    cpuFreq = psutil.cpu_freq()
    cpuPercent = psutil.cpu_percent()
    
    return cpuFreq, cpuPercent
    

#Extração dados da memória RAM

def ramData():
    ramUsed = psutil.virtual_memory().used
    ramPercent = psutil.virtual_memory().percent
    
    return ramUsed, ramPercent

#Extração dados de Disco
    
def diskData(path):
    diskUsed = psutil.disk_usage(path).used
    diskPercent = psutil.disk_usage(path).percent

    return diskUsed, diskPercent

#Extração de processos

def processData():
    for proc in psutil.process_iter([]):
        print(proc.name())
        print(proc.memory_percent())
        print(proc.cpu_percent())
        print(proc.memory_info().vms)
        

    
processData()