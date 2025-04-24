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
        cursorSelect.close()
        return False
    else:
        print("Login Realizado com Sucesso!!!")
        cursorSelect.close()
        return True

def cadastrarMaquina (hostname, macAdress, mobuId, fkCompany):
    query = f"INSERT INTO Server (hostname, macAdress, mobuId, fkCompany, status) VALUES ('{hostname}', '{macAdress}', '{mobuId}', {fkCompany});"
    cursorInsert.execute(query)
    insert.commit()
    cursorInsert.close()

def buscarMaquina (mobuId):
    query = f"SELECT idServer, hostName FROM Server WHERE mobuId = '{mobuId}';"
    cursorSelect.execute(query)

    if cursorSelect.fetchone() == None:
        print("Maquina não encontrada")
        cursorSelect.close()
        return None
    else:
        print("Maquina já cadastrada")
        cursorSelect.close()
        return cursorSelect.fetchone()[0]\


def buscarComponentes (id):
    query = f"SELECT * FROM Components WHERE fkServer = {id}"
    cursorSelect.execute(query)

def cadastrarComponentes():
    query = f"INSERT INTO Components () VALUES ('')"

