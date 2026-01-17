import random
from datetime import datetime, timedelta
from database import Database

PRODUTOS_MOCK = {
    "Cigarro": [
        ("Marlboro Red", 13.50),
        ("Marlboro Gold", 13.50),
        ("Marlboro White", 13.50),
        ("Camel Azul", 11.80),
        ("Camel Amarelo", 11.80),
        ("Camel Branco", 11.80),
        ("Lucky Strike Original", 10.90),
        ("Lucky Strike Vermelho", 10.90),
        ("Parliament", 14.20),
        ("Parliament Blue", 14.20),
        ("Winston Classic", 12.00),
        ("Winston Blue", 12.00),
        ("Benson & Hedges", 15.50),
        ("Dunhill International", 16.90),
        ("Davidoff Classic", 17.50),
        ("Hollywood", 9.50),
        ("Free", 10.20),
        ("Free Blue", 10.20),
        ("Chesterfield", 11.00),
        ("Rothmans", 12.50),
    ],
    "Charuto": [
        ("Cohiba Robusto", 65.00),
        ("Cohiba Siglo II", 75.00),
        ("Montecristo No. 2", 58.00),
        ("Montecristo No. 4", 52.00),
        ("Romeo y Julieta Churchill", 52.00),
        ("Romeo y Julieta Short Churchill", 48.00),
        ("Partagas Serie D", 48.00),
        ("Partagas Serie P", 42.00),
        ("H. Upmann Magnum", 55.00),
        ("H. Upmann Half Corona", 38.00),
        ("Punch Double Corona", 45.00),
        ("Punch Petit Coronation", 35.00),
        ("Quintero Favoritos", 28.00),
        ("Jose L. Piedra", 22.00),
        ("Vegueros", 32.00),
        ("Trinidad Reyes", 68.00),
    ],
    "Tabaco": [
        ("Tabaco American Spirit - 30g", 28.00),
        ("Tabaco Drum Original - 50g", 32.00),
        ("Tabaco Drum Blue - 50g", 32.00),
        ("Tabaco Golden Virginia - 50g", 35.00),
        ("Tabaco Golden Virginia Yellow - 50g", 35.00),
        ("Tabaco Bali Shag - 50g", 30.00),
        ("Tabaco Bali Shag Blue - 50g", 30.00),
        ("Tabaco Pueblo - 50g", 28.00),
        ("Tabaco para Cachimbo Captain Black - 50g", 42.00),
        ("Tabaco para Cachimbo Mac Baren - 50g", 48.00),
        ("Tabaco para Cachimbo Peterson - 50g", 55.00),
        ("Tabaco para Narguilé Al Fakher - 250g", 55.00),
        ("Tabaco para Narguilé Starbuzz - 250g", 65.00),
        ("Tabaco para Narguilé Adalya - 250g", 50.00),
        ("Tabaco para Narguilé Fumari - 250g", 70.00),
    ],
    "Filtro": [
        ("Piteira Longa", 4.50),
        ("Piteira Curta", 3.00),
        ("Piteira Extra Longa", 5.50),
        ("Piteira Retrátil", 6.00),
        ("Filtro Longo", 8.00),
        ("Filtro Curto", 6.50),
        ("Filtro Extra Longo", 9.50),
        ("Filtro Ativado", 10.00),
        ("Filtro Slim", 7.00),
        ("Filtro Duplo", 12.00),
    ],
    "Seda": [
        ("Seda OCB", 2.50),
        ("Seda OCB Premium", 3.50),
        ("Seda Raw", 3.00),
        ("Seda Raw Black", 3.50),
        ("Seda Smoking Brown", 2.00),
        ("Seda Smoking Red", 2.00),
        ("Seda Elements", 3.00),
        ("Seda Bambu", 4.00),
        ("Seda JOB", 2.50),
        ("Seda Zig-Zag", 2.50),
        ("Seda Pay-Pay", 2.00),
        ("Seda Bem Bolado", 2.50),
    ],
    "Acessório": [
        ("Isqueiro Zippo Clássico", 95.00),
        ("Isqueiro Zippo Windproof", 120.00),
        ("Isqueiro Zippo Slim", 110.00),
        ("Isqueiro Bic Comum", 3.50),
        ("Isqueiro Bic Maxi", 4.50),
        ("Isqueiro Clipper", 5.00),
        ("Cortador de Charuto Xikar", 85.00),
        ("Cortador de Charuto Simples", 18.00),
        ("Cortador de Charuto Duplo", 45.00),
        ("Perfurador de Charuto", 25.00),
        ("Porta-Cigarros Metálico", 55.00),
        ("Porta-Cigarros Couro", 75.00),
        ("Porta-Cigarros Alumínio", 45.00),
        ("Cachimbo Briar", 150.00),
        ("Cachimbo Corno", 45.00),
        ("Cachimbo Meerschaum", 200.00),
        ("Narguilé 1 Bocal", 180.00),
        ("Narguilé 2 Bocais", 250.00),
        ("Narguilé 4 Bocais", 350.00),
        ("Carvão para Narguilé - 1kg", 25.00),
        ("Carvão para Narguilé - 500g", 15.00),
        ("Alumínio para Narguilé", 8.00),
        ("Mangueira para Narguilé", 35.00),
        ("Bocal para Narguilé", 12.00),
    ]
}

NOMES_CLIENTES = [
    "João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Ferreira",
    "Juliana Almeida", "Roberto Souza", "Fernanda Lima", "Ricardo Martins", "Patricia Rocha",
    "Marcos Pereira", "Camila Rodrigues", "Lucas Barbosa", "Amanda Gomes", "Bruno Carvalho",
    "Larissa Araujo", "Felipe Ribeiro", "Beatriz Dias", "Gustavo Moreira", "Isabela Castro",
    "Rafael Mendes", "Carolina Costa", "Thiago Alves", "Mariana Freitas", "Gabriel Santos",
    "Leticia Rocha", "André Lima", "Vanessa Souza", "Daniel Pereira", "Juliana Costa",
    "Rodrigo Martins", "Bruna Oliveira", "Leonardo Silva", "Tatiana Almeida", "Fábio Rodrigues",
    "Renata Gomes", "Eduardo Barbosa", "Priscila Araujo", "Henrique Dias", "Monique Carvalho",
    "Vinicius Moreira", "Sabrina Castro", "Guilherme Mendes", "Natália Freitas", "Diego Alves",
    "Aline Rocha", "Paulo Santos", "Cristina Lima", "Renato Souza", "Fernanda Pereira"
]

def gerar_dados_mock(db: Database, meses_historico=12, limpar_existente=True):
    if not db.conn:
        return False
    try:
        if limpar_existente:
            db.clear_all_data()
        
        clientes_criados = []
        num_clientes = random.randint(10, len(NOMES_CLIENTES))
        clientes_selecionados = random.sample(NOMES_CLIENTES, num_clientes)
        
        for nome_cliente in clientes_selecionados:
            email = f"{nome_cliente.lower().replace(' ', '.')}@email.com" if random.random() > 0.2 else None
            telefone = f"({random.randint(11, 99)}) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}" if random.random() > 0.3 else None
            db.add_cliente(nome_cliente, email, telefone)
            db.cursor.execute("SELECT id FROM clientes WHERE nome=%s ORDER BY id DESC LIMIT 1", (nome_cliente,))
            cliente_id = db.cursor.fetchone()[0]
            clientes_criados.append(cliente_id)
        
        produtos_criados = {}
        for categoria, produtos in PRODUTOS_MOCK.items():
            for nome, preco_base in produtos:
                preco = preco_base
                margem_custo = random.uniform(0.65, 0.75)
                custo = round(preco * margem_custo, 2)
                if categoria == "Cigarro":
                    quantidade = random.randint(80, 150)
                elif categoria == "Charuto":
                    quantidade = random.randint(20, 60)
                elif categoria == "Tabaco":
                    quantidade = random.randint(30, 80)
                elif categoria == "Filtro":
                    quantidade = random.randint(100, 200)
                elif categoria == "Seda":
                    quantidade = random.randint(150, 300)
                else:
                    quantidade = random.randint(15, 50)
                db.add_produto(nome, categoria, preco, quantidade, custo)
                db.cursor.execute("SELECT id FROM produtos WHERE nome=%s AND categoria=%s ORDER BY id DESC LIMIT 1", 
                                (nome, categoria))
                produto_id = db.cursor.fetchone()[0]
                produtos_criados[produto_id] = {
                    'nome': nome,
                    'categoria': categoria,
                    'preco_base': preco_base,
                    'preco_atual': preco
                }
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=meses_historico * 30)
        total_vendas = 0
        data_atual = data_inicio
        produtos_ids = list(produtos_criados.keys())
        produtos_populares = random.sample(produtos_ids, len(produtos_ids) // 3)
        while data_atual <= data_fim:
            dia_semana = data_atual.weekday()
            num_vendas_dia = random.randint(15, 35) if dia_semana in [4, 5, 6] else random.randint(5, 20)
            mes = data_atual.month
            if mes in [1, 2]:
                num_vendas_dia = int(num_vendas_dia * 0.7)
            elif mes in [11, 12]:
                num_vendas_dia = int(num_vendas_dia * 1.3)
            for _ in range(num_vendas_dia):
                produto_id = random.choice(produtos_populares) if random.random() < 0.6 and produtos_populares else random.choice(produtos_ids)
                produto_info = produtos_criados[produto_id]
                if produto_info['categoria'] == "Cigarro":
                    quantidade = random.choices([1, 2, 3], weights=[50, 40, 10])[0]
                elif produto_info['categoria'] == "Charuto":
                    quantidade = random.choices([1, 2], weights=[90, 10])[0]
                elif produto_info['categoria'] == "Tabaco":
                    quantidade = random.choices([1, 2], weights=[80, 20])[0]
                elif produto_info['categoria'] == "Filtro":
                    quantidade = random.choices([1, 2, 3, 5], weights=[40, 35, 20, 5])[0]
                elif produto_info['categoria'] == "Seda":
                    quantidade = random.choices([1, 2, 3, 5], weights=[35, 40, 20, 5])[0]
                else:
                    quantidade = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
                if random.random() < 0.05:
                    preco_unitario = round(produto_info['preco_atual'] * 0.95, 2)
                else:
                    preco_unitario = produto_info['preco_atual']
                total = round(preco_unitario * quantidade, 2)
                hora = random.choices(range(24), weights=[1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 8, 7, 6, 7, 8, 9, 7, 5, 4, 3, 2])[0]
                data_venda = data_atual.replace(hour=hora, minute=random.randint(0, 59), second=random.randint(0, 59))
                cliente_id = random.choice(clientes_criados) if clientes_criados and random.random() > 0.25 else None
                db.add_venda(produto_id, quantidade, preco_unitario, total, data_venda, cliente_id)
                total_vendas += 1
            data_atual += timedelta(days=1)
        return True
    except Exception:
        return False

def main():
    db = Database()
    if db.connect():
        gerar_dados_mock(db, meses_historico=12, limpar_existente=True)
        db.disconnect()

if __name__ == "__main__":
    main()

