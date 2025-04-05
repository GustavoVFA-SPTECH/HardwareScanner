import mysql.connector

#Server Connection
insert = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="techpix_insert",
    password="techpix#2024",
    database="TechPix"
)
select = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="techpix_select",
    password="techpix#2024",
    database="TechPix"
)

#Cursor
cursorInsert = insert.cursor()
cursorSelect = select.cursor()

#Querys

def buscarUsuario (name, password):
    query = f"SELECT name, password FROM Employer WHERE name = '{name}' AND password = '{password}';"
    cursorSelect.execute(query)

    if cursorSelect.fetchone() == None:
        print("Usuario ou senha incorreto, por favor tente novamente !!!")
        print("Atenção, caso ainda não seja cadastrado na plataforma, cadastre-se e tente novamente ")
        return False
    else:
        print("Login Realizado com Sucesso!!!")
        return True

def cadastrarMaquina (hostname, macAdress, mobuId, fkCompany):
    query = f"INSERT INTO Server (hostname, macAdress, mobuId, fkCompany, status) VALUES ('{hostname}', '{macAdress}', '{mobuId}', {fkCompany});"
    return

def buscarMaquina (mobuId):
    query = f"SELECT idServer, hostName FROM Server WHERE mobuId = '{mobuId}';"
    cursorSelect.execute(query)

    if cursorSelect.fetchone() == None:
        print("Maquina não encontrada")
    else:
        print("Maquina já cadastrada")
