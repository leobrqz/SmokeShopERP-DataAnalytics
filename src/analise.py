from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QComboBox, QDateEdit, QGroupBox, QGridLayout, QScrollArea, QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from database import Database
from datetime import datetime
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class AnaliseWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()

    def _criar_grafico_vazio(self, titulo, figsize=(8, 4)):
        fig = Figure(figsize=figsize)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Sem dados", ha='center', va='center', transform=ax.transAxes)
        ax.set_title(titulo)
        fig.tight_layout()
        return canvas

    def _criar_grafico_linha(self, dados, titulo, xlabel, ylabel, figsize=(8, 4), mostrar_tendencia=True):
        fig = Figure(figsize=figsize)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        if dados:
            datas = [d[0] for d in dados]
            valores = [float(d[1]) for d in dados]
            ax.plot(datas, valores, marker='o', linewidth=2, markersize=4)
            if len(valores) > 1 and mostrar_tendencia:
                x_numeric = np.arange(len(valores))
                z = np.polyfit(x_numeric, valores, 1)
                p = np.poly1d(z)
                ax.plot(datas, p(x_numeric), "r--", alpha=0.5, label="Tendência")
                ax.legend()
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_title(titulo)
            ax.grid(True, alpha=0.3)
            fig.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, "Sem dados", ha='center', va='center', transform=ax.transAxes)
            ax.set_title(titulo)
        fig.tight_layout()
        return canvas

    def _criar_grafico_barra_h(self, dados, titulo, xlabel, limite_nome=20, figsize=(8, 4)):
        fig = Figure(figsize=figsize)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        if dados:
            nomes = [d[0][:limite_nome] for d in dados]
            valores = [int(d[1]) for d in dados]
            ax.barh(nomes, valores)
            ax.set_xlabel(xlabel)
            ax.set_title(titulo)
            ax.grid(True, alpha=0.3, axis='x')
        else:
            ax.text(0.5, 0.5, "Sem dados", ha='center', va='center', transform=ax.transAxes)
            ax.set_title(titulo)
        fig.tight_layout()
        return canvas

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        self.tabs_analises = QTabWidget()
        main_layout.addWidget(self.tabs_analises, 3)
        
        sidebar = QWidget()
        sidebar.setMaximumWidth(400)
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)
        
        title = QLabel("Filtros")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        sidebar_layout.addWidget(title)
        
        filters_group = QGroupBox("Filtros")
        filters_layout = QVBoxLayout()
        
        self.data_inicio = QDateEdit()
        self.data_inicio.setDate(QDate.currentDate().addMonths(-6))
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.dateChanged.connect(self.on_filtro_changed)
        filters_layout.addWidget(QLabel("Data Início:"))
        filters_layout.addWidget(self.data_inicio)
        
        self.data_fim = QDateEdit()
        self.data_fim.setDate(QDate.currentDate())
        self.data_fim.setCalendarPopup(True)
        self.data_fim.dateChanged.connect(self.on_filtro_changed)
        filters_layout.addWidget(QLabel("Data Fim:"))
        filters_layout.addWidget(self.data_fim)
        
        self.categoria = QComboBox()
        self.categoria.addItem("Todas")
        self.categoria.currentTextChanged.connect(self.on_filtro_changed)
        filters_layout.addWidget(QLabel("Categoria:"))
        filters_layout.addWidget(self.categoria)
        
        update_btn = QPushButton("Atualizar")
        update_btn.clicked.connect(self.on_filtro_changed)
        filters_layout.addWidget(update_btn)
        
        filters_group.setLayout(filters_layout)
        sidebar_layout.addWidget(filters_group)
        sidebar_layout.addStretch()
        
        main_layout.addWidget(sidebar)
        
        self.criar_tabs_categorias()
        self.load_categorias()
        self.on_filtro_changed()

    def criar_tabs_categorias(self):
        self.tabs_analises.currentChanged.connect(self.on_tab_changed)
        
        dashboard_tab = QWidget()
        self.tabs_analises.addTab(dashboard_tab, "Dashboard")
        
        temporais_tab = QWidget()
        self.tabs_analises.addTab(temporais_tab, "Temporais")
        
        produtos_tab = QWidget()
        self.tabs_analises.addTab(produtos_tab, "Produtos")
        
        estatisticas_tab = QWidget()
        self.tabs_analises.addTab(estatisticas_tab, "Estatísticas")
        
        estoque_tab = QWidget()
        self.tabs_analises.addTab(estoque_tab, "Estoque")
        
        clientes_tab = QWidget()
        self.tabs_analises.addTab(clientes_tab, "Clientes")

    def load_categorias(self):
        if not self.db.conn:
            return
        
        categorias = self.db.get_categorias()
        self.categoria.clear()
        self.categoria.addItem("Todas")
        self.categoria.addItems(categorias)

    def on_tab_changed(self, index):
        self.on_filtro_changed()

    def on_filtro_changed(self):
        if not self.db.conn:
            return
        
        data_inicio = self.data_inicio.date().toPyDate()
        data_fim = self.data_fim.date().toPyDate()
        categoria = None if self.categoria.currentText() == "Todas" else self.categoria.currentText()
        
        current_tab = self.tabs_analises.currentIndex()
        current_widget = self.tabs_analises.currentWidget()
        
        if not current_widget:
            return
        
        if current_tab == 0:
            self.mostrar_dashboard(current_widget, data_inicio, data_fim, categoria)
        elif current_tab == 1:
            self.mostrar_temporais(current_widget, data_inicio, data_fim, categoria)
        elif current_tab == 2:
            self.mostrar_produtos(current_widget, data_inicio, data_fim, categoria)
        elif current_tab == 3:
            self.mostrar_estatisticas(current_widget, data_inicio, data_fim, categoria)
        elif current_tab == 4:
            self.mostrar_estoque(current_widget, data_inicio, data_fim, categoria)
        elif current_tab == 5:
            self.mostrar_clientes(current_widget, data_inicio, data_fim, categoria)

    def mostrar_dashboard(self, widget, data_inicio, data_fim, categoria):
        layout = widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget_item = item.widget()
                if widget_item:
                    widget_item.setParent(None)
                    widget_item.deleteLater()
        else:
            layout = QVBoxLayout()
            widget.setLayout(layout)
        self.graph_layout = layout
        self.show_dashboard_completo(data_inicio, data_fim, categoria)

    def mostrar_temporais(self, widget, data_inicio, data_fim, categoria):
        layout = widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget_item = item.widget()
                if widget_item:
                    widget_item.setParent(None)
                    widget_item.deleteLater()
        else:
            layout = QVBoxLayout()
            widget.setLayout(layout)
        self.graph_layout = layout
        self.show_analises_temporais(data_inicio, data_fim, categoria)

    def mostrar_produtos(self, widget, data_inicio, data_fim, categoria):
        layout = widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget_item = item.widget()
                if widget_item:
                    widget_item.setParent(None)
                    widget_item.deleteLater()
        else:
            layout = QVBoxLayout()
            widget.setLayout(layout)
        
        tabs_produtos = QTabWidget()
        layout.addWidget(tabs_produtos)
        
        produtos_widget = QWidget()
        produtos_layout = QVBoxLayout()
        produtos_widget.setLayout(produtos_layout)
        temp_layout = self.graph_layout if hasattr(self, 'graph_layout') else None
        self.graph_layout = produtos_layout
        self.show_analise_produtos(data_inicio, data_fim, categoria)
        tabs_produtos.addTab(produtos_widget, "Análise de Produtos")
        
        margem_widget = QWidget()
        margem_layout = QVBoxLayout()
        margem_widget.setLayout(margem_layout)
        self.graph_layout = margem_layout
        self.show_analise_margem(data_inicio, data_fim, categoria)
        tabs_produtos.addTab(margem_widget, "Análise de Margem")
        
        if temp_layout is not None:
            self.graph_layout = temp_layout

    def mostrar_estatisticas(self, widget, data_inicio, data_fim, categoria):
        layout = widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget_item = item.widget()
                if widget_item:
                    widget_item.setParent(None)
                    widget_item.deleteLater()
        else:
            layout = QVBoxLayout()
            widget.setLayout(layout)
        self.graph_layout = layout
        self.show_analises_estatisticas(data_inicio, data_fim, categoria)

    def mostrar_estoque(self, widget, data_inicio, data_fim, categoria):
        layout = widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget_item = item.widget()
                if widget_item:
                    widget_item.setParent(None)
                    widget_item.deleteLater()
        else:
            layout = QVBoxLayout()
            widget.setLayout(layout)
        self.graph_layout = layout
        self.show_giro_estoque(data_inicio, data_fim, categoria)

    def mostrar_clientes(self, widget, data_inicio, data_fim, categoria):
        layout = widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget_item = item.widget()
                if widget_item:
                    widget_item.setParent(None)
                    widget_item.deleteLater()
        else:
            layout = QVBoxLayout()
            widget.setLayout(layout)
        self.graph_layout = layout
        self.show_analises_clientes(data_inicio, data_fim, categoria)

    def show_dashboard_completo(self, data_inicio, data_fim, categoria):
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        
        graphs_grid = QGridLayout()
        
        total_vendas = self.db.get_numero_vendas_periodo(data_inicio, data_fim, categoria)
        receita_total = self.db.get_total_vendas_periodo(data_inicio, data_fim, categoria)
        ticket_medio = self.db.get_ticket_medio(data_inicio, data_fim, categoria)
        
        cards_layout = QGridLayout()
        cards = [
            ("Total de Vendas", f"{total_vendas}"),
            ("Receita Total", f"R$ {receita_total:,.2f}"),
            ("Ticket Médio", f"R$ {ticket_medio:,.2f}")
        ]
        
        for i, (titulo, valor) in enumerate(cards):
            card = QGroupBox(titulo)
            card_layout = QVBoxLayout()
            label = QLabel(valor)
            label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(label)
            card.setLayout(card_layout)
            cards_layout.addWidget(card, 0, i)
        
        cards_widget = QWidget()
        cards_widget.setLayout(cards_layout)
        scroll_layout.addWidget(cards_widget)
        
        row = 1
        col = 0
        canvas1 = self._criar_grafico_linha(
            self.db.get_vendas_por_periodo(data_inicio, data_fim, categoria),
            "Vendas ao Longo do Tempo", "Data", "Vendas (R$)"
        )
        graphs_grid.addWidget(canvas1, row, col)
        col += 1
        canvas2 = self._criar_grafico_barra_h(
            self.db.get_produtos_mais_vendidos(5, False, data_inicio, data_fim, categoria),
            "Top 5 Produtos Mais Vendidos", "Quantidade", 20
        )
        graphs_grid.addWidget(canvas2, row, col)
        row += 1
        col = 0
        
        dados_receita = self.db.get_receita_por_periodo(data_inicio, data_fim, 'dia', categoria)
        fig3 = Figure(figsize=(8, 4))
        canvas3 = FigureCanvas(fig3)
        ax3 = fig3.add_subplot(111)
        if dados_receita:
            periodos = [d[0] for d in dados_receita]
            receitas = [float(d[1]) for d in dados_receita]
            ax3.bar(range(len(periodos)), receitas, alpha=0.7)
            ax3.set_xticks(range(0, len(periodos), max(1, len(periodos)//10)))
            ax3.set_xticklabels([str(p)[:10] for p in periodos[::max(1, len(periodos)//10)]], rotation=45, ha='right')
            ax3.set_xlabel("Período")
            ax3.set_ylabel("Receita (R$)")
            ax3.set_title("Receita por Período")
            ax3.grid(True, alpha=0.3, axis='y')
        else:
            ax3.text(0.5, 0.5, "Sem dados", ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title("Receita por Período")
        fig3.tight_layout()
        graphs_grid.addWidget(canvas3, row, col)
        col += 1
        vendas_dia_semana = self.db.get_vendas_por_dia_semana(data_inicio, data_fim, categoria)
        fig4 = Figure(figsize=(8, 4))
        canvas4 = FigureCanvas(fig4)
        ax4 = fig4.add_subplot(111)
        if vendas_dia_semana:
            dias_nomes = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
            dias = [int(d[0]) for d in vendas_dia_semana]
            valores = [float(d[1]) for d in vendas_dia_semana]
            ax4.bar([dias_nomes[d] for d in dias], valores, alpha=0.7)
            ax4.set_xlabel("Dia da Semana")
            ax4.set_ylabel("Vendas (R$)")
            ax4.set_title("Vendas por Dia da Semana")
            ax4.grid(True, alpha=0.3, axis='y')
        else:
            ax4.text(0.5, 0.5, "Sem dados", ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title("Vendas por Dia da Semana")
        fig4.tight_layout()
        graphs_grid.addWidget(canvas4, row, col)
        
        graphs_widget = QWidget()
        graphs_widget.setLayout(graphs_grid)
        scroll_layout.addWidget(graphs_widget)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.graph_layout.addWidget(scroll_area)

    def show_giro_estoque(self, data_inicio, data_fim, categoria):
        dados = self.db.get_giro_estoque(data_inicio, data_fim, categoria)
        
        if not dados:
            label = QLabel("Sem dados para análise de giro de estoque.")
            self.graph_layout.addWidget(label)
            return
        
        dados_ordenados = sorted(dados, key=lambda x: x['giro'], reverse=True)[:20]
        
        fig = Figure(figsize=(14, 8))
        canvas = FigureCanvas(fig)
        
        ax1 = fig.add_subplot(211)
        produtos = [d['nome'][:25] for d in dados_ordenados]
        giros = [d['giro'] for d in dados_ordenados]
        ax1.barh(produtos, giros, alpha=0.7)
        ax1.set_xlabel("Giro de Estoque")
        ax1.set_title("Top 20 Produtos - Giro de Estoque")
        ax1.grid(True, alpha=0.3, axis='x')
        
        ax2 = fig.add_subplot(212)
        dias_estoques = [min(d['dias_estoque'], 365) for d in dados_ordenados]
        ax2.barh(produtos, dias_estoques, alpha=0.7, color='orange')
        ax2.set_xlabel("Dias de Estoque Disponível")
        ax2.set_title("Dias de Estoque Disponível (Top 20)")
        ax2.grid(True, alpha=0.3, axis='x')
        
        fig.tight_layout()
        self.graph_layout.addWidget(canvas)

    def show_analises_temporais(self, data_inicio, data_fim, categoria):
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        
        graphs_grid = QGridLayout()
        
        row = 0
        col = 0
        
        vendas_dia_semana = self.db.get_vendas_por_dia_semana(data_inicio, data_fim, categoria)
        
        if vendas_dia_semana:
            fig2 = Figure(figsize=(10, 4))
            canvas2 = FigureCanvas(fig2)
            ax2 = fig2.add_subplot(111)
            dias_nomes = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
            if vendas_dia_semana:
                dias = [int(d[0]) for d in vendas_dia_semana]
                valores = [float(d[1]) for d in vendas_dia_semana]
                ax2.bar([dias_nomes[d] for d in dias], valores, alpha=0.7)
            ax2.set_xlabel("Dia da Semana")
            ax2.set_ylabel("Vendas (R$)")
            ax2.set_title("Sazonalidade - Dia da Semana")
            ax2.grid(True, alpha=0.3, axis='y')
            fig2.tight_layout()
            graphs_grid.addWidget(canvas2, row, col)
            row += 1
            col = 0
        
        tendencias = self.db.get_tendencias_produtos(data_inicio, data_fim, categoria)
        if tendencias:
            fig3 = Figure(figsize=(10, 4))
            canvas3 = FigureCanvas(fig3)
            ax3 = fig3.add_subplot(111)
            top_tendencias = sorted(tendencias, key=lambda x: abs(x['variacao']), reverse=True)[:10]
            nomes = [t['nome'][:20] for t in top_tendencias]
            variacoes = [t['variacao'] for t in top_tendencias]
            cores = ['green' if v > 0 else 'red' for v in variacoes]
            ax3.barh(nomes, variacoes, color=cores, alpha=0.7)
            ax3.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            ax3.set_xlabel("Variação Percentual (%)")
            ax3.set_title("Análise de Tendências - Top 10 Produtos")
            ax3.grid(True, alpha=0.3, axis='x')
            fig3.tight_layout()
            graphs_grid.addWidget(canvas3, row, col)
        
        graphs_widget = QWidget()
        graphs_widget.setLayout(graphs_grid)
        scroll_layout.addWidget(graphs_widget)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.graph_layout.addWidget(scroll_area)

    def show_analise_produtos(self, data_inicio, data_fim, categoria):
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        
        graphs_grid = QGridLayout()
        
        produtos_mais_vendidos = self.db.get_produtos_mais_vendidos(10, False, data_inicio, data_fim, categoria)
        if produtos_mais_vendidos:
            fig1 = Figure(figsize=(10, 5))
            canvas1 = FigureCanvas(fig1)
            ax1 = fig1.add_subplot(111)
            produtos = [d[0][:25] for d in produtos_mais_vendidos]
            quantidades = [int(d[1]) for d in produtos_mais_vendidos]
            ax1.barh(produtos, quantidades)
            ax1.set_xlabel("Quantidade Vendida")
            ax1.set_title("Top 10 Produtos Mais Vendidos")
            ax1.grid(True, alpha=0.3, axis='x')
            fig1.tight_layout()
            graphs_grid.addWidget(canvas1, 0, 0)
        
        graphs_widget = QWidget()
        graphs_widget.setLayout(graphs_grid)
        scroll_layout.addWidget(graphs_widget)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.graph_layout.addWidget(scroll_area)

    def show_analises_estatisticas(self, data_inicio, data_fim, categoria):
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        
        graphs_grid = QGridLayout()
        
        stats = self.db.get_estatisticas_descritivas(categoria)
        if stats:
            fig1 = Figure(figsize=(8, 5))
            canvas1 = FigureCanvas(fig1)
            ax1 = fig1.add_subplot(111)
            ax1.axis('off')
            titulo = "Estatísticas Descritivas - Preços"
            if categoria:
                titulo += f" ({categoria})"
            ax1.text(0.5, 0.95, titulo, ha='center', va='top', fontsize=12, fontweight='bold', transform=ax1.transAxes)
            y_pos = 0.8
            espacamento = 0.1
            estatisticas = [
                ('Total de Produtos', f"{stats['total']}"),
                ('Média', f"R$ {stats['media']:.2f}"),
                ('Mediana', f"R$ {stats['mediana']:.2f}"),
                ('Mínimo', f"R$ {stats['minimo']:.2f}"),
                ('Máximo', f"R$ {stats['maximo']:.2f}"),
                ('Desvio Padrão', f"R$ {stats['desvio_padrao']:.2f}")
            ]
            for nome, valor in estatisticas:
                ax1.text(0.3, y_pos, nome + ':', ha='right', va='center', fontsize=10, transform=ax1.transAxes)
                ax1.text(0.35, y_pos, valor, ha='left', va='center', fontsize=10, fontweight='bold', transform=ax1.transAxes)
                y_pos -= espacamento
            fig1.tight_layout()
            graphs_grid.addWidget(canvas1, 0, 0)
        
        dados_correlacao = self.db.get_correlacoes(data_inicio, data_fim, categoria)
        if dados_correlacao and len(dados_correlacao) >= 2:
            dados_validos = [(float(d[0]), float(d[1])) for d in dados_correlacao if d[0] is not None and d[1] is not None]
            if len(dados_validos) >= 2:
                precos = [d[0] for d in dados_validos]
                quantidades = [d[1] for d in dados_validos]
                correlacao = np.corrcoef(precos, quantidades)[0, 1]
                if not np.isnan(correlacao):
                    fig2 = Figure(figsize=(8, 5))
                    canvas2 = FigureCanvas(fig2)
                    ax2 = fig2.add_subplot(111)
                    ax2.scatter(precos, quantidades, alpha=0.6, s=50)
                    z = np.polyfit(precos, quantidades, 1)
                    p = np.poly1d(z)
                    ax2.plot(precos, p(precos), "r--", alpha=0.8, linewidth=2, label=f'Tendência (r={correlacao:.3f})')
                    ax2.set_xlabel("Preço (R$)")
                    ax2.set_ylabel("Quantidade Vendida")
                    ax2.set_title(f"Correlação Preço vs Quantidade\nr={correlacao:.3f}")
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                    fig2.tight_layout()
                    graphs_grid.addWidget(canvas2, 0, 1)
        
        dados_anomalias = self.db.get_vendas_por_periodo(data_inicio, data_fim, categoria)
        anomalias = self.db.get_anomalias_vendas(data_inicio, data_fim, categoria)
        if dados_anomalias:
            fig3 = Figure(figsize=(12, 5))
            canvas3 = FigureCanvas(fig3)
            ax3 = fig3.add_subplot(111)
            datas = [d[0] for d in dados_anomalias]
            valores = [float(d[1]) for d in dados_anomalias]
            ax3.plot(datas, valores, 'b-', marker='o', linewidth=1, markersize=4, label='Vendas Normais', alpha=0.6)
            if anomalias:
                anomalias_altas = [a for a in anomalias if a['tipo'] == 'alta']
                anomalias_baixas = [a for a in anomalias if a['tipo'] == 'baixa']
                if anomalias_altas:
                    datas_altas = [a['data'] for a in anomalias_altas]
                    valores_altas = [a['valor'] for a in anomalias_altas]
                    ax3.scatter(datas_altas, valores_altas, color='red', s=100, marker='^', label='Anomalias (Alta)', zorder=5)
                if anomalias_baixas:
                    datas_baixas = [a['data'] for a in anomalias_baixas]
                    valores_baixas = [a['valor'] for a in anomalias_baixas]
                    ax3.scatter(datas_baixas, valores_baixas, color='orange', s=100, marker='v', label='Anomalias (Baixa)', zorder=5)
            valores_list = valores
            if valores_list:
                media = sum(valores_list) / len(valores_list)
                variancia = sum((x - media) ** 2 for x in valores_list) / len(valores_list)
                desvio_padrao = variancia ** 0.5
                limite_superior = media + (2 * desvio_padrao)
                limite_inferior = max(0, media - (2 * desvio_padrao))
                ax3.axhline(y=media, color='green', linestyle='--', alpha=0.5, label=f'Média')
                ax3.axhline(y=limite_superior, color='red', linestyle='--', alpha=0.5, label=f'+2σ')
                ax3.axhline(y=limite_inferior, color='orange', linestyle='--', alpha=0.5, label=f'-2σ')
            ax3.set_xlabel("Data")
            ax3.set_ylabel("Vendas (R$)")
            ax3.set_title(f"Detecção de Anomalias\n{len(anomalias)} anomalias detectadas")
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            fig3.autofmt_xdate()
            fig3.tight_layout()
            graphs_grid.addWidget(canvas3, 1, 0, 1, 2)
        
        graphs_widget = QWidget()
        graphs_widget.setLayout(graphs_grid)
        scroll_layout.addWidget(graphs_widget)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.graph_layout.addWidget(scroll_area)

    def show_analise_margem(self, data_inicio, data_fim, categoria):
        dados = self.db.get_analise_margem(data_inicio, data_fim, categoria)
        if not dados:
            canvas = self._criar_grafico_vazio("Análise de Margem\n(Sem dados)")
            self.graph_layout.addWidget(canvas)
            return
        
        produtos = []
        for d in dados:
            produtos.append({
                'nome': d[1][:30],
                'categoria': d[2],
                'preco': float(d[3]),
                'custo': float(d[4]),
                'margem_unit': float(d[5]),
                'margem_percent': float(d[6]),
                'quantidade': float(d[7]),
                'receita': float(d[8]),
                'custo_total': float(d[9]),
                'lucro': float(d[10])
            })
        
        top_10 = produtos[:10]
        
        fig = Figure(figsize=(14, 10))
        canvas = FigureCanvas(fig)
        
        ax1 = fig.add_subplot(221)
        nomes = [p['nome'] for p in top_10]
        lucros = [p['lucro'] for p in top_10]
        ax1.barh(nomes, lucros)
        ax1.set_xlabel("Lucro Total (R$)")
        ax1.set_title("Top 10 Produtos por Lucro")
        ax1.grid(True, alpha=0.3, axis='x')
        fig.autofmt_xdate()
        
        ax2 = fig.add_subplot(222)
        margens = [p['margem_percent'] for p in top_10]
        ax2.barh(nomes, margens, color='green')
        ax2.set_xlabel("Margem (%)")
        ax2.set_title("Top 10 Produtos por Margem %")
        ax2.grid(True, alpha=0.3, axis='x')
        fig.autofmt_xdate()
        
        ax3 = fig.add_subplot(223)
        precos = [p['preco'] for p in produtos]
        custos = [p['custo'] for p in produtos]
        ax3.scatter(precos, custos, alpha=0.6, s=50)
        ax3.plot([0, max(precos)], [0, max(precos)], 'r--', alpha=0.5, label='Linha de Equilíbrio')
        ax3.set_xlabel("Preço (R$)")
        ax3.set_ylabel("Custo (R$)")
        ax3.set_title("Preço vs Custo")
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        ax4 = fig.add_subplot(224)
        ax4.axis('off')
        ax4.text(0.1, 0.9, "Resumo de Rentabilidade", ha='left', va='top', 
                fontsize=12, fontweight='bold', transform=ax4.transAxes)
        y_pos = 0.8
        
        receita_total = sum([p['receita'] for p in produtos])
        custo_total = sum([p['custo_total'] for p in produtos])
        lucro_total = sum([p['lucro'] for p in produtos])
        margem_media = np.mean([p['margem_percent'] for p in produtos if p['margem_percent'] > 0])
        
        resumo = [
            ("Receita Total", f"R$ {receita_total:,.2f}"),
            ("Custo Total", f"R$ {custo_total:,.2f}"),
            ("Lucro Total", f"R$ {lucro_total:,.2f}"),
            ("Margem Média", f"{margem_media:.2f}%")
        ]
        
        for nome, valor in resumo:
            ax4.text(0.1, y_pos, f"{nome}: {valor}", ha='left', va='top', 
                    fontsize=10, transform=ax4.transAxes)
            y_pos -= 0.12
        
        fig.tight_layout()
        self.graph_layout.addWidget(canvas)

    def show_analises_clientes(self, data_inicio, data_fim, categoria):
        tabs_clientes = QTabWidget()
        
        overview_scroll = QScrollArea()
        overview_scroll.setWidgetResizable(True)
        overview_widget = QWidget()
        overview_layout = QVBoxLayout()
        overview_widget.setLayout(overview_layout)
        overview_scroll.setWidget(overview_widget)
        
        stats = self.db.get_estatisticas_clientes(data_inicio, data_fim)
        if stats:
            fig_stats = Figure(figsize=(12, 2.5))
            canvas_stats = FigureCanvas(fig_stats)
            ax_stats = fig_stats.add_subplot(111)
            ax_stats.axis('off')
            ax_stats.text(0.5, 0.95, "Estatísticas de Clientes", ha='center', va='top', 
                         fontsize=12, fontweight='bold', transform=ax_stats.transAxes)
            y_pos = 0.65
            estatisticas = [
                ('Total de Clientes', f"{stats['total_clientes']}"),
                ('Clientes com Compras', f"{stats['clientes_com_compras']}"),
                ('Total de Vendas', f"{stats['total_vendas']}"),
                ('Receita Total', f"R$ {stats['receita_total']:,.2f}"),
                ('Ticket Médio Geral', f"R$ {stats['ticket_medio_geral']:,.2f}")
            ]
            for nome, valor in estatisticas:
                ax_stats.text(0.3, y_pos, nome + ':', ha='right', va='center', 
                            fontsize=10, transform=ax_stats.transAxes)
                ax_stats.text(0.35, y_pos, valor, ha='left', va='center', 
                            fontsize=10, fontweight='bold', transform=ax_stats.transAxes)
                y_pos -= 0.18
            fig_stats.tight_layout(pad=2.0)
            overview_layout.addWidget(canvas_stats)
        
        clientes_frequentes = self.db.get_clientes_mais_frequentes(8, data_inicio, data_fim)
        if clientes_frequentes:
            fig1 = Figure(figsize=(10, 5))
            canvas1 = FigureCanvas(fig1)
            ax1 = fig1.add_subplot(111)
            nomes = [c[1][:20] + "..." if len(c[1]) > 20 else c[1] for c in clientes_frequentes]
            compras = [c[2] for c in clientes_frequentes]
            ax1.barh(nomes, compras, alpha=0.7)
            ax1.set_xlabel("Número de Compras", fontsize=10)
            ax1.set_title("Top 8 Clientes Mais Frequentes", fontsize=11)
            ax1.tick_params(axis='y', labelsize=9)
            ax1.tick_params(axis='x', labelsize=9)
            ax1.grid(True, alpha=0.3, axis='x')
            fig1.tight_layout(pad=2.5)
            overview_layout.addWidget(canvas1)
        
        tabs_clientes.addTab(overview_scroll, "Visão Geral")
        
        detalhes_scroll = QScrollArea()
        detalhes_scroll.setWidgetResizable(True)
        detalhes_widget = QWidget()
        detalhes_layout = QVBoxLayout()
        detalhes_widget.setLayout(detalhes_layout)
        detalhes_scroll.setWidget(detalhes_widget)
        
        clientes_ticket = self.db.get_clientes_maior_ticket_medio(8, data_inicio, data_fim)
        if clientes_ticket:
            fig3 = Figure(figsize=(10, 5))
            canvas3 = FigureCanvas(fig3)
            ax3 = fig3.add_subplot(111)
            nomes = [c[1][:20] + "..." if len(c[1]) > 20 else c[1] for c in clientes_ticket]
            tickets = [float(c[4]) for c in clientes_ticket]
            ax3.barh(nomes, tickets, alpha=0.7, color='orange')
            ax3.set_xlabel("Ticket Médio (R$)", fontsize=10)
            ax3.set_title("Top 8 Clientes por Ticket Médio", fontsize=11)
            ax3.tick_params(axis='y', labelsize=9)
            ax3.tick_params(axis='x', labelsize=9)
            ax3.grid(True, alpha=0.3, axis='x')
            fig3.tight_layout(pad=2.5)
            detalhes_layout.addWidget(canvas3)
        
        vendas_por_cliente = self.db.get_vendas_por_cliente(data_inicio, data_fim)
        if vendas_por_cliente and len(vendas_por_cliente) > 0:
            fig4 = Figure(figsize=(10, 5))
            canvas4 = FigureCanvas(fig4)
            ax4 = fig4.add_subplot(111)
            nomes = [v[1][:20] + "..." if len(v[1]) > 20 else v[1] for v in vendas_por_cliente[:10]]
            receitas = [float(v[3]) for v in vendas_por_cliente[:10]]
            ax4.barh(nomes, receitas, alpha=0.7, color='steelblue')
            ax4.set_xlabel("Receita Total (R$)", fontsize=10)
            ax4.set_title("Receita por Cliente (Top 10)", fontsize=11)
            ax4.tick_params(axis='y', labelsize=9)
            ax4.tick_params(axis='x', labelsize=9)
            ax4.grid(True, alpha=0.3, axis='x')
            fig4.tight_layout(pad=2.5)
            detalhes_layout.addWidget(canvas4)
        
        tabs_clientes.addTab(detalhes_scroll, "Detalhes")
        
        self.graph_layout.addWidget(tabs_clientes)

    def refresh_data(self):
        self.load_categorias()
        self.on_filtro_changed()

