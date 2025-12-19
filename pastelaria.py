import sqlite3


def setup_database():
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            categoria TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(mesa_id) REFERENCES mesas(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedido_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY(item_id) REFERENCES itens(id)
        )
    ''')

    conn.commit()
    conn.close()


class Item:
    def __init__(self, nome, preco, categoria):
        self.nome = nome
        self.preco = preco
        self.categoria = categoria

class Pedido:
    def __init__(self, mesa_id, status='aberto'):
        self.mesa_id = mesa_id
        self.status = status

class Mesa:
    def __init__(self, numero):
        self.numero = numero


def cadastrar_mesa(numero):
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO mesas (numero) VALUES (?)', (numero,))
    conn.commit()
    conn.close()

def cadastrar_item(nome, preco, categoria):
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO itens (nome, preco, categoria) VALUES (?, ?, ?)', (nome, preco, categoria))
    conn.commit()
    conn.close()

def listar_itens():
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM itens')
    itens = cursor.fetchall()
    conn.close()
    print('=== Cardápio ===')
    for item in itens:
        print(f'ID: {item[0]} | Nome: {item[1]} | Preço: R${item[2]:.2f} | Categoria: {item[3]}')

def criar_pedido(mesa_id):
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pedidos (mesa_id, status) VALUES (?, ?)', (mesa_id, 'aberto'))
    conn.commit()
    conn.close()
    print('Pedido criado com sucesso!')

def alocar_item_pedido(pedido_id, item_id, quantidade):
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pedido_itens (pedido_id, item_id, quantidade) VALUES (?, ?, ?)', (pedido_id, item_id, quantidade))
    conn.commit()
    conn.close()
    print('Item alocado ao pedido com sucesso!')

def fechar_pedido(mesa_id):
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, i.nome, i.preco, pi.quantidade 
        FROM pedidos p
        JOIN pedido_itens pi ON p.id = pi.pedido_id
        JOIN itens i ON pi.item_id = i.id
        WHERE p.mesa_id = ? AND p.status = 'aberto'
    ''', (mesa_id,))
    pedidos = cursor.fetchall()

    if not pedidos:
        print('Nenhum pedido aberto para esta mesa.')
        conn.close()
        return

    total = sum(preco * quantidade for _, _, preco, quantidade in pedidos)
    print(f'\n=== Conta da Mesa {mesa_id} ===')
    for pedido_id, nome, preco, quantidade in pedidos:
        print(f'{quantidade}x {nome} (R${preco:.2f})')
    print(f'Total: R${total:.2f}\n')

    cursor.execute('UPDATE pedidos SET status = ? WHERE mesa_id = ?', ('fechado', mesa_id))
    conn.commit()
    conn.close()
    print('Pedido fechado com sucesso!')

def listar_mesas():
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mesas')
    mesas = cursor.fetchall()
    conn.close()
    print('=== Mesas ===')
    for mesa in mesas:
        print(f'ID: {mesa[0]} | Número: {mesa[1]}')

def listar_pedidos_abertos():
    conn = sqlite3.connect('pastelaria.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pedidos WHERE status = "aberto"')
    pedidos = cursor.fetchall()
    conn.close()
    print('=== Pedidos Abertos ===')
    for pedido in pedidos:
        print(f'ID: {pedido[0]} | Mesa ID: {pedido[1]} | Status: {pedido[2]}')


def menu():
    setup_database()
    while True:
        print('''
=== Pastelaria Gourmet ===
1. Cadastrar mesa
2. Cadastrar item no cardápio
3. Listar itens do cardápio
4. Criar pedido para mesa
5. Alocar item ao pedido
6. Fechar pedido e exibir conta
7. Listar mesas
8. Listar pedidos abertos
0. Sair
        ''')
        opcao = input('Escolha uma opção: ')
        if opcao == '1':
            numero = input('Número da mesa: ')
            cadastrar_mesa(numero)
        elif opcao == '2':
            nome = input('Nome do item: ')
            preco = float(input('Preço: '))
            categoria = input('Categoria (Pastel/Bebida/Sobremesa): ')
            cadastrar_item(nome, preco, categoria)
        elif opcao == '3':
            listar_itens()
        elif opcao == '4':
            mesa_id = int(input('ID da mesa: '))
            criar_pedido(mesa_id)
        elif opcao == '5':
            pedido_id = int(input('ID do pedido: '))
            item_id = int(input('ID do item: '))
            quantidade = int(input('Quantidade: '))
            alocar_item_pedido(pedido_id, item_id, quantidade)
        elif opcao == '6':
            mesa_id = int(input('ID da mesa: '))
            fechar_pedido(mesa_id)
        elif opcao == '7':
            listar_mesas()
        elif opcao == '8':
            listar_pedidos_abertos()
        elif opcao == '0':
            print('Saindo...')
            break
        else:
            print('Opção inválida!')

if __name__ == '__main__':
    menu()
