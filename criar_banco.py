import sqlite3

connection = sqlite3.connect('hotels.db')
cursor = connection.cursor()

criar_tabela = '''CREATE TABLE IF NOT EXISTS hoteis (
            id integer PRIMARY KEY AUTOINCREMENT, 
            nome text,
            estrelas real,
            valor_diaria real,
            cidade text
            )'''

cursor.execute(criar_tabela)
connection.commit()
connection.close()
