import os
import time
from setup import getHostname, getMacAddress, getMobuId, so, sync_components, buscarUsuario, buscarMaquina, cadastrarMaquina
from extract import monitor_and_send

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def login():
    clear_screen()
    print("=== TechPix - Sistema de Monitoramento ===")
    print("\nPor favor, faça login")

    while True:
        username = input("Usuário: ")
        password = input("Senha: ")

        user_data = buscarUsuario(username, password)
        if user_data:
            # A função buscarUsuario agora retorna (success, company_id, company_name)
            return username, user_data[1], user_data[2]  # username, company_id, company_name
        else:
            print("\nCredenciais inválidas. Tente novamente.\n")

def register_machine(username, company_id):
    clear_screen()
    print("=== Validação de Máquina ===")

    hostname = getHostname(so)
    mac_address = getMacAddress(so)
    mobu_id = getMobuId(so)

    print(f"\nDetectamos os seguintes dados da sua máquina:")
    print(f"Hostname: {hostname}")
    print(f"Endereço MAC: {mac_address}")
    print(f"ID da Placa-Mãe: {mobu_id}")

    machine_id = buscarMaquina(mobu_id, company_id)

    if machine_id is None:
        print("\nEsta máquina não está cadastrada no sistema.")
        confirm = input("Deseja cadastrá-la agora? (S/N): ").strip().upper()

        if confirm == 'S':
            # A função cadastrarMaquina agora retorna o machine_id diretamente
            machine_id = cadastrarMaquina(hostname, mac_address, mobu_id, company_id)
            if machine_id:
                print("Máquina cadastrada com sucesso!")
            else:
                print("Falha ao cadastrar máquina. Tente novamente.")
                time.sleep(2)
                return register_machine(username, company_id)
        else:
            print("O cadastro da máquina é necessário para continuar.")
            time.sleep(2)
            return register_machine(username, company_id)

    # A função sync_components foi adaptada para usar a API
    if sync_components(machine_id, company_id, so):
        print("Componentes sincronizados com sucesso!")
    else:
        print("Aviso: Falha ao sincronizar componentes")

    return machine_id

def configure_limits(machine_id):
    clear_screen()
    print("=== Configuração de Limites ===")

    limits = {
        'cpu_percent': 80,
        'cpu_freq': None,
        'ram_percent': 80,
        'disk_percent': 80
    }

    print("\nConfigure os limites de utilização para cada componente:")

    try:
        limits['cpu_percent'] = int(input("Limite de uso da CPU (%): ") or 80)
        limits['cpu_freq'] = int(input("Limite de frequência da CPU (MHz): ") or 0)
        limits['ram_percent'] = int(input("Limite de uso de RAM (%): ") or 80)
        limits['disk_percent'] = int(input("Limite de uso de Disco (%): ") or 80)
    except ValueError:
        print("Valor inválido. Usando valores padrão.")
        time.sleep(2)

    return limits

def main():
    api_url = "http://44.208.193.41:5000/s3/raw/upload"

    # Agora o login retorna também o company_name
    username, company_id, company_name = login()
    machine_id = register_machine(username, company_id)
    limits = configure_limits(machine_id)

    clear_screen()
    print(f"=== Monitoramento Ativo - {company_name} ===")
    print("\nConfigurações atuais:")
    print(f"- Limite CPU: {limits['cpu_percent']}%")
    if limits['cpu_freq']:
        print(f"- Frequência máxima CPU: {limits['cpu_freq']}MHz")
    print(f"- Limite RAM: {limits['ram_percent']}%")
    print(f"- Limite Disco: {limits['disk_percent']}%")
    print("\nPressione Ctrl+C para parar o monitoramento...")

    mobu_id = getMobuId(so)

    try:
        monitor_and_send(company_name, mobu_id, api_url)
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuário.")
    except Exception as e:
        print(f"\nErro durante o monitoramento: {str(e)}")

if __name__ == "__main__":
    main()