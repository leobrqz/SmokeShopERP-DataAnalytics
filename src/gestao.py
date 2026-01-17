from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QComboBox, QDateEdit, QMessageBox, QTabWidget, QGroupBox, QStackedWidget
)
from PyQt6.QtCore import Qt, QDate, QPoint
from PyQt6.QtGui import QFont
from database import Database
from datetime import datetime

class ComboBoxLimitado(QComboBox):
    def __init__(self, max_items=10, parent=None):
        super().__init__(parent)
        self.max_items = max_items
        self.setMaxVisibleItems(max_items)
    
    def showPopup(self):
        super().showPopup()
        view = self.view()
        if view:
            model = view.model()
            if model and model.rowCount() > 0:
                item_height = view.sizeHintForRow(0)
            else:
                item_height = 20
            max_height = item_height * self.max_items + 2
            view.setMaximumHeight(max_height)
            popup = self.view().window()
            if popup:
                popup.setMaximumHeight(max_height + 10)
                pos = self.mapToGlobal(QPoint(0, self.height()))
                popup.move(pos)

class GestaoWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.selected_produto_id = None
        self.selected_venda_id = None
        self.selected_cliente_id = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        self.tabs_principais = QTabWidget()
        self.tabs_principais.currentChanged.connect(self.on_tab_principal_changed)
        
        produtos_widget = QWidget()
        produtos_layout = QVBoxLayout()
        produtos_widget.setLayout(produtos_layout)
        
        produtos_filters = QGroupBox("Filtros")
        produtos_filters_layout = QHBoxLayout()
        self.produto_filtro_categoria = QComboBox()
        self.produto_filtro_categoria.addItem("Todas")
        self.produto_filtro_categoria.currentTextChanged.connect(self.apply_produto_filters)
        produtos_filters_layout.addWidget(QLabel("Categoria:"))
        produtos_filters_layout.addWidget(self.produto_filtro_categoria)
        produtos_filters_layout.addStretch()
        produtos_filters.setLayout(produtos_filters_layout)
        produtos_layout.addWidget(produtos_filters)
        
        self.table_produtos = QTableWidget()
        self.table_produtos.setAlternatingRowColors(True)
        self.table_produtos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_produtos.itemSelectionChanged.connect(self.on_produto_selected)
        produtos_layout.addWidget(self.table_produtos, 1)
        
        self.tabs_principais.addTab(produtos_widget, "Produtos")
        
        vendas_widget = QWidget()
        vendas_layout = QVBoxLayout()
        vendas_widget.setLayout(vendas_layout)
        
        vendas_filters = QGroupBox("Filtros")
        vendas_filters_layout = QHBoxLayout()
        self.venda_filtro_categoria = QComboBox()
        self.venda_filtro_categoria.addItem("Todas")
        self.venda_filtro_categoria.currentTextChanged.connect(self.apply_venda_filters)
        self.venda_filtro_data_inicio = QDateEdit()
        self.venda_filtro_data_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.venda_filtro_data_inicio.setCalendarPopup(True)
        self.venda_filtro_data_fim = QDateEdit()
        self.venda_filtro_data_fim.setDate(QDate.currentDate())
        self.venda_filtro_data_fim.setCalendarPopup(True)
        self.btn_atualizar_vendas = QPushButton("Atualizar")
        self.btn_atualizar_vendas.clicked.connect(self.apply_venda_filters)
        vendas_filters_layout.addWidget(QLabel("Categoria:"))
        vendas_filters_layout.addWidget(self.venda_filtro_categoria)
        vendas_filters_layout.addWidget(QLabel("Data Início:"))
        vendas_filters_layout.addWidget(self.venda_filtro_data_inicio)
        vendas_filters_layout.addWidget(QLabel("Data Fim:"))
        vendas_filters_layout.addWidget(self.venda_filtro_data_fim)
        vendas_filters_layout.addWidget(self.btn_atualizar_vendas)
        vendas_filters_layout.addStretch()
        vendas_filters.setLayout(vendas_filters_layout)
        vendas_layout.addWidget(vendas_filters)
        
        self.table_vendas = QTableWidget()
        self.table_vendas.setAlternatingRowColors(True)
        self.table_vendas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_vendas.itemSelectionChanged.connect(self.on_venda_selected)
        vendas_layout.addWidget(self.table_vendas, 1)
        
        self.tabs_principais.addTab(vendas_widget, "Vendas")
        
        clientes_widget = QWidget()
        clientes_layout = QVBoxLayout()
        clientes_widget.setLayout(clientes_layout)
        
        clientes_filters = QGroupBox("Filtros")
        clientes_filters_layout = QHBoxLayout()
        clientes_filters_layout.addStretch()
        clientes_filters.setLayout(clientes_filters_layout)
        clientes_layout.addWidget(clientes_filters)
        
        self.table_clientes = QTableWidget()
        self.table_clientes.setAlternatingRowColors(True)
        self.table_clientes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_clientes.itemSelectionChanged.connect(self.on_cliente_selected)
        clientes_layout.addWidget(self.table_clientes, 1)
        
        self.tabs_principais.addTab(clientes_widget, "Clientes")
        
        main_layout.addWidget(self.tabs_principais, 3)
        
        sidebar = QWidget()
        sidebar.setMaximumWidth(400)
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)
        
        self.stacked_sidebar = QStackedWidget()
        
        produtos_tab = QWidget()
        produtos_layout = QVBoxLayout()
        produtos_tab.setLayout(produtos_layout)
        
        produtos_title = QLabel("Produto")
        produtos_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        produtos_layout.addWidget(produtos_title)
        
        self.produto_nome = QLineEdit()
        produtos_layout.addWidget(QLabel("Nome:"))
        produtos_layout.addWidget(self.produto_nome)
        
        self.produto_categoria = QComboBox()
        self.produto_categoria.setEditable(True)
        self.produto_categoria.addItems(["Cigarro", "Charuto", "Tabaco", "Acessório"])
        produtos_layout.addWidget(QLabel("Categoria:"))
        produtos_layout.addWidget(self.produto_categoria)
        
        self.produto_preco = QLineEdit()
        produtos_layout.addWidget(QLabel("Preço:"))
        produtos_layout.addWidget(self.produto_preco)
        
        self.produto_quantidade = QLineEdit()
        produtos_layout.addWidget(QLabel("Quantidade:"))
        produtos_layout.addWidget(self.produto_quantidade)
        
        btn_layout = QHBoxLayout()
        add_prod_btn = QPushButton("Adicionar")
        add_prod_btn.clicked.connect(self.add_produto)
        save_prod_btn = QPushButton("Salvar")
        save_prod_btn.clicked.connect(self.save_produto)
        delete_prod_btn = QPushButton("Excluir")
        delete_prod_btn.clicked.connect(self.delete_produto)
        
        btn_layout.addWidget(add_prod_btn)
        btn_layout.addWidget(save_prod_btn)
        btn_layout.addWidget(delete_prod_btn)
        produtos_layout.addLayout(btn_layout)
        produtos_layout.addStretch()
        self.stacked_sidebar.addWidget(produtos_tab)
        
        vendas_tab = QWidget()
        vendas_layout = QVBoxLayout()
        vendas_tab.setLayout(vendas_layout)
        
        vendas_title = QLabel("Venda")
        vendas_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        vendas_layout.addWidget(vendas_title)
        
        self.venda_produto = ComboBoxLimitado(max_items=10)
        vendas_layout.addWidget(QLabel("Produto:"))
        vendas_layout.addWidget(self.venda_produto)
        self.venda_produto.currentIndexChanged.connect(self.on_produto_selected_for_venda)
        
        self.venda_quantidade = QLineEdit()
        vendas_layout.addWidget(QLabel("Quantidade:"))
        vendas_layout.addWidget(self.venda_quantidade)
        self.venda_quantidade.textChanged.connect(self.calculate_venda_total)
        
        self.venda_preco_unit = QLineEdit()
        vendas_layout.addWidget(QLabel("Preço Unitário:"))
        vendas_layout.addWidget(self.venda_preco_unit)
        self.venda_preco_unit.textChanged.connect(self.calculate_venda_total)
        
        self.venda_data = QDateEdit()
        self.venda_data.setDate(QDate.currentDate())
        self.venda_data.setCalendarPopup(True)
        vendas_layout.addWidget(QLabel("Data da Venda:"))
        vendas_layout.addWidget(self.venda_data)
        
        self.venda_total = QLineEdit()
        self.venda_total.setReadOnly(True)
        vendas_layout.addWidget(QLabel("Total:"))
        vendas_layout.addWidget(self.venda_total)
        
        btn_layout_v = QHBoxLayout()
        add_venda_btn = QPushButton("Adicionar")
        add_venda_btn.clicked.connect(self.add_venda)
        save_venda_btn = QPushButton("Salvar")
        save_venda_btn.clicked.connect(self.save_venda)
        delete_venda_btn = QPushButton("Excluir")
        delete_venda_btn.clicked.connect(self.delete_venda)
        
        btn_layout_v.addWidget(add_venda_btn)
        btn_layout_v.addWidget(save_venda_btn)
        btn_layout_v.addWidget(delete_venda_btn)
        vendas_layout.addLayout(btn_layout_v)
        self.venda_cliente = ComboBoxLimitado(max_items=10)
        self.venda_cliente.addItem("Cliente não informado", None)
        vendas_layout.addWidget(QLabel("Cliente:"))
        vendas_layout.addWidget(self.venda_cliente)
        
        vendas_layout.addStretch()
        self.stacked_sidebar.addWidget(vendas_tab)
        
        clientes_tab = QWidget()
        clientes_layout = QVBoxLayout()
        clientes_tab.setLayout(clientes_layout)
        
        clientes_title = QLabel("Cliente")
        clientes_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        clientes_layout.addWidget(clientes_title)
        
        self.cliente_nome = QLineEdit()
        clientes_layout.addWidget(QLabel("Nome:"))
        clientes_layout.addWidget(self.cliente_nome)
        
        self.cliente_email = QLineEdit()
        clientes_layout.addWidget(QLabel("Email:"))
        clientes_layout.addWidget(self.cliente_email)
        
        self.cliente_telefone = QLineEdit()
        clientes_layout.addWidget(QLabel("Telefone:"))
        clientes_layout.addWidget(self.cliente_telefone)
        
        btn_layout_c = QHBoxLayout()
        add_cliente_btn = QPushButton("Adicionar")
        add_cliente_btn.clicked.connect(self.add_cliente)
        save_cliente_btn = QPushButton("Salvar")
        save_cliente_btn.clicked.connect(self.save_cliente)
        delete_cliente_btn = QPushButton("Excluir")
        delete_cliente_btn.clicked.connect(self.delete_cliente)
        
        btn_layout_c.addWidget(add_cliente_btn)
        btn_layout_c.addWidget(save_cliente_btn)
        btn_layout_c.addWidget(delete_cliente_btn)
        clientes_layout.addLayout(btn_layout_c)
        clientes_layout.addStretch()
        self.stacked_sidebar.addWidget(clientes_tab)
        
        sidebar_layout.addWidget(self.stacked_sidebar)
        
        main_layout.addWidget(sidebar)
        
        self.load_produtos_combo()
        self.load_categorias_filtros()
        self.on_tab_principal_changed(0)

    def on_tab_principal_changed(self, index):
        if index == 0:
            if hasattr(self, 'stacked_sidebar'):
                self.stacked_sidebar.setCurrentIndex(0)
            self.load_produtos_table()
        elif index == 1:
            if hasattr(self, 'stacked_sidebar'):
                self.stacked_sidebar.setCurrentIndex(1)
            self.load_vendas_table()
        else:
            if hasattr(self, 'stacked_sidebar'):
                self.stacked_sidebar.setCurrentIndex(2)
            self.load_clientes_table()

    def load_produtos_table(self):
        if not self.db.conn:
            return
        self.apply_produto_filters()
    
    def on_produto_selected(self):
        selected = self.table_produtos.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        produto_id = int(self.table_produtos.item(row, 0).text())
        self.load_produto_details(produto_id)
        if hasattr(self, 'stacked_sidebar'):
            self.stacked_sidebar.setCurrentIndex(0)
    
    def apply_produto_filters(self):
        if not self.db.conn:
            return
        
        todos_produtos = self.db.get_produtos()
        categoria_filtro = self.produto_filtro_categoria.currentText()
        
        if categoria_filtro != "Todas":
            produtos_filtrados = [p for p in todos_produtos if len(p) > 2 and p[2] == categoria_filtro]
        else:
            produtos_filtrados = todos_produtos
        
        produtos_validos = [p for p in produtos_filtrados if len(p) >= 5]
        
        self.table_produtos.clear()
        self.table_produtos.setRowCount(0)
        self.table_produtos.setColumnCount(5)
        self.table_produtos.setHorizontalHeaderLabels(["ID", "Nome", "Categoria", "Preço", "Quantidade"])
        
        for col in range(5):
            self.table_produtos.showColumn(col)
        
        if produtos_validos:
            self.table_produtos.setRowCount(len(produtos_validos))
            for i, produto in enumerate(produtos_validos):
                for j, value in enumerate(produto):
                    self.table_produtos.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
        
        self.table_produtos.hideColumn(0)
        self.table_produtos.resizeColumnsToContents()

    def load_vendas_table(self):
        if not self.db.conn:
            return
        self.apply_venda_filters()
    
    def on_venda_selected(self):
        selected = self.table_vendas.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        venda_id = int(self.table_vendas.item(row, 0).text())
        self.load_venda_details(venda_id)
        if hasattr(self, 'stacked_sidebar'):
            self.stacked_sidebar.setCurrentIndex(1)
    
    def apply_venda_filters(self):
        if not self.db.conn:
            return
        
        todas_vendas = self.db.get_vendas()
        
        categoria_filtro = self.venda_filtro_categoria.currentText()
        data_inicio_date = self.venda_filtro_data_inicio.date().toPyDate()
        data_fim_date = self.venda_filtro_data_fim.date().toPyDate()
        data_inicio = datetime.combine(data_inicio_date, datetime.min.time())
        data_fim = datetime.combine(data_fim_date, datetime.max.time())
        
        vendas_filtradas = []
        
        for venda in todas_vendas:
            if len(venda) < 10:
                continue
                
            venda_id, produto_id, nome, categoria, quantidade, preco_unit, total, data_venda, cliente_id, cliente_nome = venda
            
            filtro_categoria_ok = True
            if categoria_filtro != "Todas":
                filtro_categoria_ok = (categoria == categoria_filtro)
            
            filtro_data_ok = True
            if data_venda:
                try:
                    if isinstance(data_venda, datetime):
                        data_venda_dt = data_venda
                    else:
                        data_venda_str = str(data_venda)
                        if '.' in data_venda_str:
                            data_venda_str = data_venda_str.split('.')[0]
                        if ' ' in data_venda_str:
                            data_venda_dt = datetime.strptime(data_venda_str, "%Y-%m-%d %H:%M:%S")
                        else:
                            data_venda_dt = datetime.combine(datetime.strptime(data_venda_str, "%Y-%m-%d").date(), datetime.min.time())
                    
                    filtro_data_ok = (data_inicio <= data_venda_dt <= data_fim)
                except Exception:
                    filtro_data_ok = True
            
            if filtro_categoria_ok and filtro_data_ok:
                vendas_filtradas.append(venda)
        
        self.table_vendas.setColumnCount(10)
        self.table_vendas.setRowCount(len(vendas_filtradas))
        self.table_vendas.setHorizontalHeaderLabels(
            ["ID", "Produto ID", "Produto", "Categoria", "Quantidade", "Preço Unit.", "Total", "Data", "Cliente ID", "Cliente"]
        )
        
        for i, venda in enumerate(vendas_filtradas):
            for j, value in enumerate(venda):
                if j == 7:
                    if isinstance(value, datetime):
                        self.table_vendas.setItem(i, j, QTableWidgetItem(value.strftime("%d/%m/%Y %H:%M")))
                    else:
                        self.table_vendas.setItem(i, j, QTableWidgetItem(str(value)))
                else:
                    self.table_vendas.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
        
        self.table_vendas.hideColumn(0)
        self.table_vendas.hideColumn(1)
        self.table_vendas.hideColumn(8)
        self.table_vendas.resizeColumnsToContents()

    def on_cliente_selected(self):
        selected = self.table_clientes.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        cliente_id = int(self.table_clientes.item(row, 0).text())
        self.load_cliente_details(cliente_id)
        if hasattr(self, 'stacked_sidebar'):
            self.stacked_sidebar.setCurrentIndex(2)

    def load_produto_details(self, produto_id):
        produto = self.db.get_produto(produto_id)
        if produto:
            self.selected_produto_id = produto_id
            self.produto_nome.setText(produto[1])
            index = self.produto_categoria.findText(produto[2] if produto[2] else "")
            if index >= 0:
                self.produto_categoria.setCurrentIndex(index)
            else:
                self.produto_categoria.setCurrentText(produto[2] if produto[2] else "")
            self.produto_preco.setText(str(produto[3]))
            self.produto_quantidade.setText(str(produto[4]))

    def load_venda_details(self, venda_id):
        venda = self.db.get_venda(venda_id)
        if venda:
            self.selected_venda_id = venda_id
            produto_id = venda[1]
            for i in range(self.venda_produto.count()):
                if self.venda_produto.itemData(i) == produto_id:
                    self.venda_produto.setCurrentIndex(i)
                    break
            
            cliente_id = venda[7] if len(venda) >= 8 else None
            if cliente_id:
                for i in range(self.venda_cliente.count()):
                    if self.venda_cliente.itemData(i) == cliente_id:
                        self.venda_cliente.setCurrentIndex(i)
                        break
            else:
                self.venda_cliente.setCurrentIndex(0)
            
            self.venda_quantidade.setText(str(venda[3]))
            self.venda_preco_unit.setText(str(venda[4]))
            if isinstance(venda[6], datetime):
                self.venda_data.setDate(QDate.fromString(venda[6].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.calculate_venda_total()

    def add_produto(self):
        if not self.db.conn:
            QMessageBox.warning(self, "Erro", "Não conectado ao banco de dados.")
            return
        try:
            self.db.add_produto(
                self.produto_nome.text(),
                self.produto_categoria.currentText(),
                float(self.produto_preco.text()),
                int(self.produto_quantidade.text())
            )
            QMessageBox.information(self, "Sucesso", "Produto adicionado!")
            self.clear_produto_form()
            self.load_categorias_filtros()
            self.load_produtos_combo()
            self.load_produtos_table()
        except (ValueError, Exception):
            QMessageBox.warning(self, "Erro", "Erro ao adicionar produto.")

    def save_produto(self):
        if not self.db.conn or not self.selected_produto_id:
            QMessageBox.warning(self, "Erro", "Selecione um produto para atualizar.")
            return
        try:
            self.db.update_produto(
                self.selected_produto_id,
                self.produto_nome.text(),
                self.produto_categoria.currentText(),
                float(self.produto_preco.text()),
                int(self.produto_quantidade.text())
            )
            QMessageBox.information(self, "Sucesso", "Produto atualizado!")
            self.clear_produto_form()
            self.load_categorias_filtros()
            self.load_produtos_combo()
            self.load_produtos_table()
        except (ValueError, Exception):
            QMessageBox.warning(self, "Erro", "Erro ao atualizar produto.")

    def delete_produto(self):
        if not self.db.conn or not self.selected_produto_id:
            QMessageBox.warning(self, "Erro", "Selecione um produto para excluir.")
            return
        reply = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir este produto?")
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_produto(self.selected_produto_id)
            QMessageBox.information(self, "Sucesso", "Produto excluído!")
            self.clear_produto_form()
            self.load_categorias_filtros()
            self.load_produtos_combo()
            self.load_produtos_table()

    def clear_produto_form(self):
        self.produto_nome.clear()
        self.produto_categoria.setCurrentIndex(0)
        self.produto_preco.clear()
        self.produto_quantidade.clear()
        self.selected_produto_id = None

    def load_produtos_combo(self):
        if not self.db.conn:
            return
        
        produtos = self.db.get_produtos()
        self.venda_produto.clear()
        
        for produto in produtos:
            self.venda_produto.addItem(f"{produto[1]} (R$ {produto[3]:.2f})", produto[0])
        
        self.load_clientes_combo()

    def on_produto_selected_for_venda(self):
        if self.venda_produto.currentData():
            produto_id = self.venda_produto.currentData()
            produto = self.db.get_produto(produto_id)
            if produto:
                self.venda_preco_unit.setText(str(produto[3]))
                self.calculate_venda_total()

    def calculate_venda_total(self):
        try:
            self.venda_total.setText(f"{float(self.venda_quantidade.text() or 0) * float(self.venda_preco_unit.text() or 0):.2f}")
        except (ValueError, Exception):
            self.venda_total.setText("0.00")

    def add_venda(self):
        if not self.db.conn:
            QMessageBox.warning(self, "Erro", "Não conectado ao banco de dados.")
            return
        produto_id = self.venda_produto.currentData()
        if not produto_id:
            QMessageBox.warning(self, "Erro", "Selecione um produto.")
            return
        try:
            cliente_id = self.venda_cliente.currentData()
            data_venda = datetime.combine(self.venda_data.date().toPyDate(), datetime.min.time())
            self.db.add_venda(
                produto_id,
                int(self.venda_quantidade.text()),
                float(self.venda_preco_unit.text()),
                float(self.venda_total.text()),
                data_venda,
                cliente_id
            )
            QMessageBox.information(self, "Sucesso", "Venda adicionada!")
            self.clear_venda_form()
            self.load_vendas_table()
        except (ValueError, Exception):
            QMessageBox.warning(self, "Erro", "Erro ao adicionar venda.")

    def save_venda(self):
        if not self.db.conn or not self.selected_venda_id:
            QMessageBox.warning(self, "Erro", "Selecione uma venda para atualizar.")
            return
        try:
            cliente_id = self.venda_cliente.currentData()
            data_venda = datetime.combine(self.venda_data.date().toPyDate(), datetime.min.time())
            self.db.update_venda(
                self.selected_venda_id,
                self.venda_produto.currentData(),
                int(self.venda_quantidade.text()),
                float(self.venda_preco_unit.text()),
                float(self.venda_total.text()),
                data_venda,
                cliente_id
            )
            QMessageBox.information(self, "Sucesso", "Venda atualizada!")
            self.clear_venda_form()
            self.load_vendas_table()
        except (ValueError, Exception):
            QMessageBox.warning(self, "Erro", "Erro ao atualizar venda.")

    def delete_venda(self):
        if not self.db.conn or not self.selected_venda_id:
            QMessageBox.warning(self, "Erro", "Selecione uma venda para excluir.")
            return
        reply = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir esta venda?")
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_venda(self.selected_venda_id)
            QMessageBox.information(self, "Sucesso", "Venda excluída!")
            self.clear_venda_form()
            self.load_vendas_table()

    def clear_venda_form(self):
        if self.venda_produto.count() > 0:
            self.venda_produto.setCurrentIndex(0)
        self.venda_quantidade.clear()
        self.venda_preco_unit.clear()
        self.venda_data.setDate(QDate.currentDate())
        self.venda_total.clear()
        self.selected_venda_id = None

    def load_categorias_filtros(self):
        if not self.db.conn:
            return
        
        categorias = self.db.get_categorias()
        
        texto_atual_produto = self.produto_filtro_categoria.currentText()
        self.produto_filtro_categoria.blockSignals(True)
        self.produto_filtro_categoria.clear()
        self.produto_filtro_categoria.addItem("Todas")
        if categorias:
            self.produto_filtro_categoria.addItems(categorias)
        if texto_atual_produto and texto_atual_produto in ["Todas"] + categorias:
            index = self.produto_filtro_categoria.findText(texto_atual_produto)
            if index >= 0:
                self.produto_filtro_categoria.setCurrentIndex(index)
            else:
                self.produto_filtro_categoria.setCurrentIndex(0)
        else:
            self.produto_filtro_categoria.setCurrentIndex(0)
        self.produto_filtro_categoria.blockSignals(False)
        
        texto_atual_venda = self.venda_filtro_categoria.currentText()
        self.venda_filtro_categoria.blockSignals(True)
        self.venda_filtro_categoria.clear()
        self.venda_filtro_categoria.addItem("Todas")
        if categorias:
            self.venda_filtro_categoria.addItems(categorias)
        if texto_atual_venda and texto_atual_venda in ["Todas"] + categorias:
            index = self.venda_filtro_categoria.findText(texto_atual_venda)
            if index >= 0:
                self.venda_filtro_categoria.setCurrentIndex(index)
            else:
                self.venda_filtro_categoria.setCurrentIndex(0)
        else:
            self.venda_filtro_categoria.setCurrentIndex(0)
        self.venda_filtro_categoria.blockSignals(False)
    
    def load_clientes_combo(self):
        if not self.db.conn:
            return
        
        clientes = self.db.get_clientes()
        self.venda_cliente.clear()
        self.venda_cliente.addItem("Cliente não informado", None)
        
        for cliente in clientes:
            self.venda_cliente.addItem(cliente[1], cliente[0])

    def load_clientes_table(self):
        if not self.db.conn:
            return
        
        clientes = self.db.get_clientes()
        
        self.table_clientes.setColumnCount(5)
        self.table_clientes.setRowCount(len(clientes))
        self.table_clientes.setHorizontalHeaderLabels(["ID", "Nome", "Email", "Telefone", "Data Cadastro"])
        
        for i, cliente in enumerate(clientes):
            for j, value in enumerate(cliente):
                if j == 4 and isinstance(value, datetime):
                    self.table_clientes.setItem(i, j, QTableWidgetItem(value.strftime("%d/%m/%Y")))
                else:
                    self.table_clientes.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
        
        self.table_clientes.hideColumn(0)
        self.table_clientes.resizeColumnsToContents()

    def load_cliente_details(self, cliente_id):
        cliente = self.db.get_cliente(cliente_id)
        if cliente:
            self.selected_cliente_id = cliente_id
            self.cliente_nome.setText(cliente[1])
            self.cliente_email.setText(cliente[2] if cliente[2] else "")
            self.cliente_telefone.setText(cliente[3] if cliente[3] else "")

    def add_cliente(self):
        if not self.db.conn:
            QMessageBox.warning(self, "Erro", "Não conectado ao banco de dados.")
            return
        try:
            self.db.add_cliente(
                self.cliente_nome.text(),
                self.cliente_email.text() if self.cliente_email.text() else None,
                self.cliente_telefone.text() if self.cliente_telefone.text() else None
            )
            QMessageBox.information(self, "Sucesso", "Cliente adicionado!")
            self.clear_cliente_form()
            self.load_clientes_combo()
            self.load_clientes_table()
        except (ValueError, Exception):
            QMessageBox.warning(self, "Erro", "Erro ao adicionar cliente.")

    def save_cliente(self):
        if not self.db.conn or not self.selected_cliente_id:
            QMessageBox.warning(self, "Erro", "Selecione um cliente para atualizar.")
            return
        try:
            self.db.update_cliente(
                self.selected_cliente_id,
                self.cliente_nome.text(),
                self.cliente_email.text() if self.cliente_email.text() else None,
                self.cliente_telefone.text() if self.cliente_telefone.text() else None
            )
            QMessageBox.information(self, "Sucesso", "Cliente atualizado!")
            self.clear_cliente_form()
            self.load_clientes_combo()
            self.load_clientes_table()
        except (ValueError, Exception):
            QMessageBox.warning(self, "Erro", "Erro ao atualizar cliente.")

    def delete_cliente(self):
        if not self.db.conn or not self.selected_cliente_id:
            QMessageBox.warning(self, "Erro", "Selecione um cliente para excluir.")
            return
        reply = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir este cliente?")
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_cliente(self.selected_cliente_id)
            QMessageBox.information(self, "Sucesso", "Cliente excluído!")
            self.clear_cliente_form()
            self.load_clientes_combo()
            self.load_clientes_table()

    def clear_cliente_form(self):
        self.cliente_nome.clear()
        self.cliente_email.clear()
        self.cliente_telefone.clear()
        self.selected_cliente_id = None

    def refresh_data(self):
        self.load_categorias_filtros()
        self.load_produtos_combo()
        self.load_clientes_combo()
        if hasattr(self, 'tabs_principais'):
            self.on_tab_principal_changed(self.tabs_principais.currentIndex())

