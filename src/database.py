import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class Database:
    def __init__(self, dbname="TabacariaDB", user="postgres", password=None, host="localhost", port="5432"):
        self.dbname = dbname
        self.user = user
        self.password = password or os.getenv("DB_PASSWORD", "")
        self.host = host
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            self.init_tables()
            return True
        except Exception:
            return False

    def init_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                categoria VARCHAR(100),
                preco DECIMAL(10,2) NOT NULL,
                custo DECIMAL(10,2) DEFAULT 0,
                quantidade INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            self.cursor.execute("ALTER TABLE produtos ADD COLUMN IF NOT EXISTS custo DECIMAL(10,2) DEFAULT 0")
            self.conn.commit()
        except Exception:
            pass
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                telefone VARCHAR(20),
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                produto_id INTEGER REFERENCES produtos(id),
                cliente_id INTEGER REFERENCES clientes(id),
                quantidade INTEGER NOT NULL,
                preco_unitario DECIMAL(10,2) NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                data_venda TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            self.cursor.execute("ALTER TABLE vendas ADD COLUMN IF NOT EXISTS cliente_id INTEGER REFERENCES clientes(id)")
            self.conn.commit()
        except Exception:
            pass
        self.conn.commit()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_produtos(self):
        self.cursor.execute("SELECT id, nome, categoria, preco, COALESCE(custo, 0), quantidade FROM produtos ORDER BY id")
        return self.cursor.fetchall()

    def get_produto(self, produto_id):
        self.cursor.execute("SELECT id, nome, categoria, preco, COALESCE(custo, 0), quantidade FROM produtos WHERE id=%s", (produto_id,))
        return self.cursor.fetchone()

    def add_produto(self, nome, categoria, preco, quantidade, custo=0):
        self.cursor.execute("""
            INSERT INTO produtos (nome, categoria, preco, custo, quantidade)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, categoria, preco, custo, quantidade))
        self.conn.commit()

    def update_produto(self, produto_id, nome, categoria, preco, quantidade, custo=0):
        self.cursor.execute("""
            UPDATE produtos SET nome=%s, categoria=%s, preco=%s, custo=%s, quantidade=%s
            WHERE id=%s
        """, (nome, categoria, preco, custo, quantidade, produto_id))
        self.conn.commit()

    def delete_produto(self, produto_id):
        self.cursor.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
        self.conn.commit()

    def get_clientes(self):
        self.cursor.execute("SELECT id, nome, email, telefone, data_cadastro FROM clientes ORDER BY nome")
        return self.cursor.fetchall()

    def get_cliente(self, cliente_id):
        self.cursor.execute("SELECT id, nome, email, telefone, data_cadastro FROM clientes WHERE id=%s", (cliente_id,))
        return self.cursor.fetchone()

    def add_cliente(self, nome, email=None, telefone=None):
        self.cursor.execute("""
            INSERT INTO clientes (nome, email, telefone)
            VALUES (%s, %s, %s)
        """, (nome, email, telefone))
        self.conn.commit()

    def update_cliente(self, cliente_id, nome, email=None, telefone=None):
        self.cursor.execute("""
            UPDATE clientes SET nome=%s, email=%s, telefone=%s
            WHERE id=%s
        """, (nome, email, telefone, cliente_id))
        self.conn.commit()

    def delete_cliente(self, cliente_id):
        self.cursor.execute("UPDATE vendas SET cliente_id = NULL WHERE cliente_id = %s", (cliente_id,))
        self.cursor.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
        self.conn.commit()

    def get_vendas(self):
        self.cursor.execute("""
            SELECT v.id, v.produto_id, p.nome, p.categoria, v.quantidade, 
                   v.preco_unitario, v.total, v.data_venda, v.cliente_id,
                   COALESCE(c.nome, 'Cliente não informado') as cliente_nome
            FROM vendas v
            LEFT JOIN produtos p ON v.produto_id = p.id
            LEFT JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.data_venda DESC
        """)
        return self.cursor.fetchall()

    def get_venda(self, venda_id):
        self.cursor.execute("""
            SELECT v.id, v.produto_id, p.nome, v.quantidade, 
                   v.preco_unitario, v.total, v.data_venda, v.cliente_id
            FROM vendas v
            LEFT JOIN produtos p ON v.produto_id = p.id
            WHERE v.id=%s
        """, (venda_id,))
        return self.cursor.fetchone()

    def add_venda(self, produto_id, quantidade, preco_unitario, total, data_venda, cliente_id=None):
        self.cursor.execute("""
            INSERT INTO vendas (produto_id, cliente_id, quantidade, preco_unitario, total, data_venda)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (produto_id, cliente_id, quantidade, preco_unitario, total, data_venda))
        self.cursor.execute("""
            UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s
        """, (quantidade, produto_id))
        self.conn.commit()

    def update_venda(self, venda_id, produto_id, quantidade, preco_unitario, total, data_venda, cliente_id=None):
        self.cursor.execute("SELECT produto_id, quantidade FROM vendas WHERE id=%s", (venda_id,))
        old = self.cursor.fetchone()
        if old:
            old_produto_id, old_quantidade = old
            self.cursor.execute("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s", 
                              (old_quantidade, old_produto_id))
        self.cursor.execute("""
            UPDATE vendas SET produto_id=%s, cliente_id=%s, quantidade=%s, preco_unitario=%s, total=%s, data_venda=%s
            WHERE id=%s
        """, (produto_id, cliente_id, quantidade, preco_unitario, total, data_venda, venda_id))
        self.cursor.execute("UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s", 
                          (quantidade, produto_id))
        self.conn.commit()

    def delete_venda(self, venda_id):
        self.cursor.execute("SELECT produto_id, quantidade FROM vendas WHERE id=%s", (venda_id,))
        old = self.cursor.fetchone()
        if old:
            produto_id, quantidade = old
            self.cursor.execute("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s", 
                              (quantidade, produto_id))
        self.cursor.execute("DELETE FROM vendas WHERE id=%s", (venda_id,))
        self.conn.commit()

    def get_vendas_por_periodo(self, data_inicio, data_fim, categoria=None):
        if categoria:
            self.cursor.execute("""
                SELECT DATE(v.data_venda), SUM(v.total)
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s AND p.categoria = %s
                GROUP BY DATE(v.data_venda)
                ORDER BY DATE(v.data_venda)
            """, (data_inicio, data_fim, categoria))
        else:
            self.cursor.execute("""
                SELECT DATE(data_venda), SUM(total)
                FROM vendas
                WHERE data_venda BETWEEN %s AND %s
                GROUP BY DATE(data_venda)
                ORDER BY DATE(data_venda)
            """, (data_inicio, data_fim))
        return self.cursor.fetchall()

    def get_produtos_mais_vendidos(self, limite=10, por_receita=False, data_inicio=None, data_fim=None, categoria=None):
        query = f"""
            SELECT p.nome, {'SUM(v.total)' if por_receita else 'SUM(v.quantidade)'} as total
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
        """
        conditions = []
        params = []
        if data_inicio and data_fim:
            conditions.append("v.data_venda BETWEEN %s AND %s")
            params.extend([data_inicio, data_fim])
        if categoria:
            conditions.append("p.categoria = %s")
            params.append(categoria)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += """
            GROUP BY p.id, p.nome
            ORDER BY total DESC
            LIMIT %s
        """
        params.append(limite)
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    def get_total_vendas_periodo(self, data_inicio, data_fim, categoria=None):
        if categoria:
            self.cursor.execute("""
                SELECT SUM(v.total) FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s AND p.categoria = %s
            """, (data_inicio, data_fim, categoria))
        else:
            self.cursor.execute("""
                SELECT SUM(total) FROM vendas
                WHERE data_venda BETWEEN %s AND %s
            """, (data_inicio, data_fim))
        result = self.cursor.fetchone()
        return result[0] if result and result[0] else 0

    def get_numero_vendas_periodo(self, data_inicio, data_fim, categoria=None):
        if categoria:
            self.cursor.execute("""
                SELECT COUNT(*) FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s AND p.categoria = %s
            """, (data_inicio, data_fim, categoria))
        else:
            self.cursor.execute("""
                SELECT COUNT(*) FROM vendas
                WHERE data_venda BETWEEN %s AND %s
            """, (data_inicio, data_fim))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_ticket_medio(self, data_inicio, data_fim, categoria=None):
        total = self.get_total_vendas_periodo(data_inicio, data_fim, categoria)
        num_vendas = self.get_numero_vendas_periodo(data_inicio, data_fim, categoria)
        return total / num_vendas if num_vendas > 0 else 0

    def get_receita_por_periodo(self, data_inicio, data_fim, agrupamento='dia', categoria=None):
        group_map = {
            'dia': "DATE(data_venda)",
            'semana': "DATE_TRUNC('week', data_venda)",
            'mes': "DATE_TRUNC('month', data_venda)"
        }
        group_by = group_map.get(agrupamento, "DATE(data_venda)")
        if categoria:
            self.cursor.execute(f"""
                SELECT {group_by}, SUM(v.total)
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s AND p.categoria = %s
                GROUP BY {group_by}
                ORDER BY {group_by}
            """, (data_inicio, data_fim, categoria))
        else:
            self.cursor.execute(f"""
                SELECT {group_by}, SUM(total)
                FROM vendas
                WHERE data_venda BETWEEN %s AND %s
                GROUP BY {group_by}
                ORDER BY {group_by}
            """, (data_inicio, data_fim))
        return self.cursor.fetchall()

    def get_vendas_por_dia_semana(self, data_inicio, data_fim, categoria=None):
        if categoria:
            self.cursor.execute("""
                SELECT EXTRACT(DOW FROM v.data_venda) as dia_semana, SUM(v.total)
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s AND p.categoria = %s
                GROUP BY EXTRACT(DOW FROM v.data_venda)
                ORDER BY dia_semana
            """, (data_inicio, data_fim, categoria))
        else:
            self.cursor.execute("""
                SELECT EXTRACT(DOW FROM data_venda) as dia_semana, SUM(total)
                FROM vendas
                WHERE data_venda BETWEEN %s AND %s
                GROUP BY EXTRACT(DOW FROM data_venda)
                ORDER BY dia_semana
            """, (data_inicio, data_fim))
        return self.cursor.fetchall()

    def get_tendencias_produtos(self, data_inicio, data_fim, categoria=None):
        periodo_meio = data_inicio + (data_fim - data_inicio) / 2
        if categoria:
            self.cursor.execute("""
                SELECT p.id, p.nome, SUM(v.quantidade) as total
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s AND p.categoria = %s
                GROUP BY p.id, p.nome
            """, (data_inicio, periodo_meio, categoria))
            primeira_metade = {row[0]: row[2] for row in self.cursor.fetchall()}
            self.cursor.execute("""
                SELECT p.id, p.nome, SUM(v.quantidade) as total
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s AND p.categoria = %s
                GROUP BY p.id, p.nome
            """, (periodo_meio, data_fim, categoria))
            segunda_metade = {row[0]: row[2] for row in self.cursor.fetchall()}
        else:
            self.cursor.execute("""
                SELECT produto_id, SUM(quantidade) as total
                FROM vendas
                WHERE data_venda BETWEEN %s AND %s
                GROUP BY produto_id
            """, (data_inicio, periodo_meio))
            primeira_metade = {row[0]: row[1] for row in self.cursor.fetchall()}
            self.cursor.execute("""
                SELECT produto_id, SUM(quantidade) as total
                FROM vendas
                WHERE data_venda BETWEEN %s AND %s
                GROUP BY produto_id
            """, (periodo_meio, data_fim))
            segunda_metade = {row[0]: row[1] for row in self.cursor.fetchall()}
        tendencias = []
        todos_ids = set(primeira_metade.keys()) | set(segunda_metade.keys())
        for produto_id in todos_ids:
            primeira = primeira_metade.get(produto_id, 0)
            segunda = segunda_metade.get(produto_id, 0)
            variacao = ((segunda - primeira) / primeira) * 100 if primeira > 0 else (100 if segunda > 0 else 0)
            self.cursor.execute("SELECT nome FROM produtos WHERE id=%s", (produto_id,))
            nome = self.cursor.fetchone()
            nome = nome[0] if nome else f"Produto {produto_id}"
            tendencias.append({
                'id': produto_id,
                'nome': nome,
                'primeira_metade': primeira,
                'segunda_metade': segunda,
                'variacao': variacao
            })
        return sorted(tendencias, key=lambda x: x['variacao'], reverse=True)

    def get_categorias(self):
        self.cursor.execute("SELECT DISTINCT categoria FROM produtos WHERE categoria IS NOT NULL ORDER BY categoria")
        return [row[0] for row in self.cursor.fetchall()]

    def get_giro_estoque(self, data_inicio, data_fim, categoria=None):
        if categoria:
            self.cursor.execute("""
                SELECT 
                    p.id,
                    p.nome,
                    p.quantidade as estoque_atual,
                    COALESCE(SUM(v.quantidade), 0) as quantidade_vendida,
                    p.preco
                FROM produtos p
                LEFT JOIN vendas v ON p.id = v.produto_id 
                    AND v.data_venda BETWEEN %s AND %s
                WHERE p.categoria = %s
                GROUP BY p.id, p.nome, p.quantidade, p.preco
            """, (data_inicio, data_fim, categoria))
        else:
            self.cursor.execute("""
                SELECT 
                    p.id,
                    p.nome,
                    p.quantidade as estoque_atual,
                    COALESCE(SUM(v.quantidade), 0) as quantidade_vendida,
                    p.preco
                FROM produtos p
                LEFT JOIN vendas v ON p.id = v.produto_id 
                    AND v.data_venda BETWEEN %s AND %s
                GROUP BY p.id, p.nome, p.quantidade, p.preco
            """, (data_inicio, data_fim))
        
        produtos = self.cursor.fetchall()
        resultado = []
        
        dias_periodo = (data_fim - data_inicio).days
        if dias_periodo == 0:
            dias_periodo = 1
        
        for produto_id, nome, estoque_atual, quantidade_vendida, preco in produtos:
            estoque_medio = float(estoque_atual) if estoque_atual else 0
            quantidade_vendida = float(quantidade_vendida) if quantidade_vendida else 0
            
            if estoque_medio > 0:
                giro = quantidade_vendida / estoque_medio
            else:
                giro = 0
            
            media_diaria = quantidade_vendida / dias_periodo if dias_periodo > 0 else 0
            
            if media_diaria > 0:
                dias_estoque = estoque_medio / media_diaria
            else:
                dias_estoque = 999 if estoque_medio > 0 else 0
            
            resultado.append({
                'id': produto_id,
                'nome': nome,
                'estoque_atual': estoque_medio,
                'quantidade_vendida': quantidade_vendida,
                'giro': giro,
                'dias_estoque': dias_estoque,
                'preco': float(preco) if preco else 0
            })
        
        return resultado

    def get_estatisticas_descritivas(self, categoria=None):
        if categoria:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(preco) as media,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco) as mediana,
                    MIN(preco) as minimo,
                    MAX(preco) as maximo,
                    STDDEV(preco) as desvio_padrao
                FROM produtos
                WHERE categoria = %s
            """, (categoria,))
        else:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(preco) as media,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco) as mediana,
                    MIN(preco) as minimo,
                    MAX(preco) as maximo,
                    STDDEV(preco) as desvio_padrao
                FROM produtos
            """)
        
        result = self.cursor.fetchone()
        if result and result[0]:
            return {
                'total': result[0],
                'media': float(result[1]) if result[1] else 0,
                'mediana': float(result[2]) if result[2] else 0,
                'minimo': float(result[3]) if result[3] else 0,
                'maximo': float(result[4]) if result[4] else 0,
                'desvio_padrao': float(result[5]) if result[5] else 0
            }
        return None

    def get_anomalias_vendas(self, data_inicio, data_fim, categoria=None):
        dados = self.get_vendas_por_periodo(data_inicio, data_fim, categoria)
        
        if not dados or len(dados) < 3:
            return []
        
        valores = [float(d[1]) for d in dados]
        media = sum(valores) / len(valores)
        variancia = sum((x - media) ** 2 for x in valores) / len(valores)
        desvio_padrao = variancia ** 0.5
        
        limite_superior = media + (2 * desvio_padrao)
        limite_inferior = max(0, media - (2 * desvio_padrao))
        
        anomalias = []
        for data, valor in dados:
            valor_float = float(valor)
            if valor_float > limite_superior or valor_float < limite_inferior:
                anomalias.append({
                    'data': data,
                    'valor': valor_float,
                    'media': media,
                    'desvio': abs(valor_float - media) / desvio_padrao if desvio_padrao > 0 else 0,
                    'tipo': 'alta' if valor_float > limite_superior else 'baixa'
                })
        
        return anomalias

    def get_correlacoes(self, data_inicio, data_fim, categoria=None):
        if categoria:
            self.cursor.execute("""
                SELECT 
                    p.preco,
                    SUM(v.quantidade) as quantidade_total
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s AND p.categoria = %s
                GROUP BY p.id, p.preco
            """, (data_inicio, data_fim, categoria))
        else:
            self.cursor.execute("""
                SELECT 
                    p.preco,
                    SUM(v.quantidade) as quantidade_total
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.data_venda BETWEEN %s AND %s
                GROUP BY p.id, p.preco
            """, (data_inicio, data_fim))
        
        return self.cursor.fetchall()

    def get_analise_margem(self, data_inicio, data_fim, categoria=None):
        if categoria:
            self.cursor.execute("""
                SELECT 
                    p.id,
                    p.nome,
                    p.categoria,
                    p.preco,
                    COALESCE(p.custo, 0) as custo,
                    (p.preco - COALESCE(p.custo, 0)) as margem_unit,
                    ((p.preco - COALESCE(p.custo, 0)) / NULLIF(p.preco, 0) * 100) as margem_percent,
                    COALESCE(SUM(v.quantidade), 0) as quantidade_vendida,
                    COALESCE(SUM(v.total), 0) as receita_total,
                    (COALESCE(SUM(v.quantidade), 0) * COALESCE(p.custo, 0)) as custo_total,
                    (COALESCE(SUM(v.total), 0) - (COALESCE(SUM(v.quantidade), 0) * COALESCE(p.custo, 0))) as lucro_total
                FROM produtos p
                LEFT JOIN vendas v ON p.id = v.produto_id 
                    AND v.data_venda BETWEEN %s AND %s
                WHERE p.categoria = %s
                GROUP BY p.id, p.nome, p.categoria, p.preco, p.custo
                ORDER BY lucro_total DESC
            """, (data_inicio, data_fim, categoria))
        else:
            self.cursor.execute("""
                SELECT 
                    p.id,
                    p.nome,
                    p.categoria,
                    p.preco,
                    COALESCE(p.custo, 0) as custo,
                    (p.preco - COALESCE(p.custo, 0)) as margem_unit,
                    ((p.preco - COALESCE(p.custo, 0)) / NULLIF(p.preco, 0) * 100) as margem_percent,
                    COALESCE(SUM(v.quantidade), 0) as quantidade_vendida,
                    COALESCE(SUM(v.total), 0) as receita_total,
                    (COALESCE(SUM(v.quantidade), 0) * COALESCE(p.custo, 0)) as custo_total,
                    (COALESCE(SUM(v.total), 0) - (COALESCE(SUM(v.quantidade), 0) * COALESCE(p.custo, 0))) as lucro_total
                FROM produtos p
                LEFT JOIN vendas v ON p.id = v.produto_id 
                    AND v.data_venda BETWEEN %s AND %s
                GROUP BY p.id, p.nome, p.categoria, p.preco, p.custo
                ORDER BY lucro_total DESC
            """, (data_inicio, data_fim))
        return self.cursor.fetchall()

    def get_clientes_mais_frequentes(self, limite=10, data_inicio=None, data_fim=None):
        query = """
            SELECT c.id, c.nome, COUNT(v.id) as num_compras, SUM(v.total) as total_gasto
            FROM clientes c
            LEFT JOIN vendas v ON c.id = v.cliente_id
        """
        conditions = []
        params = []
        if data_inicio and data_fim:
            conditions.append("v.data_venda BETWEEN %s AND %s")
            params.extend([data_inicio, data_fim])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += """
            GROUP BY c.id, c.nome
            HAVING COUNT(v.id) > 0
            ORDER BY num_compras DESC, total_gasto DESC
            LIMIT %s
        """
        params.append(limite)
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    def get_clientes_maior_ticket_medio(self, limite=10, data_inicio=None, data_fim=None):
        query = """
            SELECT c.id, c.nome, COUNT(v.id) as num_compras, 
                   SUM(v.total) as total_gasto, AVG(v.total) as ticket_medio
            FROM clientes c
            LEFT JOIN vendas v ON c.id = v.cliente_id
        """
        conditions = []
        params = []
        if data_inicio and data_fim:
            conditions.append("v.data_venda BETWEEN %s AND %s")
            params.extend([data_inicio, data_fim])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += """
            GROUP BY c.id, c.nome
            HAVING COUNT(v.id) > 0
            ORDER BY ticket_medio DESC
            LIMIT %s
        """
        params.append(limite)
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    def get_vendas_por_cliente(self, data_inicio, data_fim):
        self.cursor.execute("""
            SELECT 
                c.id,
                c.nome,
                COUNT(v.id) as num_vendas,
                SUM(v.total) as receita_total,
                AVG(v.total) as ticket_medio,
                MIN(v.data_venda) as primeira_compra,
                MAX(v.data_venda) as ultima_compra
            FROM clientes c
            LEFT JOIN vendas v ON c.id = v.cliente_id 
                AND v.data_venda BETWEEN %s AND %s
            GROUP BY c.id, c.nome
            HAVING COUNT(v.id) > 0
            ORDER BY receita_total DESC
        """, (data_inicio, data_fim))
        return self.cursor.fetchall()

    def get_estatisticas_clientes(self, data_inicio=None, data_fim=None):
        query = """
            SELECT 
                COUNT(DISTINCT c.id) as total_clientes,
                COUNT(DISTINCT v.cliente_id) as clientes_com_compras,
                COUNT(v.id) as total_vendas,
                SUM(v.total) as receita_total,
                AVG(v.total) as ticket_medio_geral
            FROM clientes c
            LEFT JOIN vendas v ON c.id = v.cliente_id
        """
        params = []
        if data_inicio and data_fim:
            query += " WHERE v.data_venda BETWEEN %s AND %s"
            params.extend([data_inicio, data_fim])
        self.cursor.execute(query, tuple(params))
        result = self.cursor.fetchone()
        if result:
            return {
                'total_clientes': result[0] or 0,
                'clientes_com_compras': result[1] or 0,
                'total_vendas': result[2] or 0,
                'receita_total': float(result[3]) if result[3] else 0,
                'ticket_medio_geral': float(result[4]) if result[4] else 0
            }
        return None

    def clear_all_data(self):
        self.cursor.execute("DELETE FROM vendas")
        self.cursor.execute("DELETE FROM produtos")
        self.cursor.execute("DELETE FROM clientes")
        self.conn.commit()

