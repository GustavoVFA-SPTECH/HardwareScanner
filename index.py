import requests

url = 'http://exemplo.com/upload'
arquivo = {'arquivo': open('meu_arquivo.txt', 'rb')}

response = requests.post(url, files=arquivo)

print(response.status_code)
print(response.text)