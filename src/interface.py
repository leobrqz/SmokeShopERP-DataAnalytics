from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QDialog, QDialogButtonBox, QStackedWidget,
    QLineEdit, QFormLayout, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from database import Database
from gestao import GestaoWidget
from analise import AnaliseWidget

def aplicar_tema_claro(app):
    app.setStyle("Fusion")
    
    palette = QPalette()
    
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)

def aplicar_tema_escuro(app):
    app.setStyle("Fusion")
    
    palette = QPalette()
    
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    
    app.setPalette(palette)

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conectar Banco de Dados")
        self.setModal(True)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.dbname_input = QLineEdit("TabacariaDB")
        self.user_input = QLineEdit("postgres")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.host_input = QLineEdit("localhost")
        self.port_input = QLineEdit("5432")
        
        form_layout.addRow("Banco:", self.dbname_input)
        form_layout.addRow("Usuário:", self.user_input)
        form_layout.addRow("Senha:", self.password_input)
        form_layout.addRow("Host:", self.host_input)
        form_layout.addRow("Porta:", self.port_input)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_section = "gestao"
        self.tema_claro = True
        self.init_ui()
        self.try_connect()

    def init_ui(self):
        self.setWindowTitle("Tabacaria - Sistema de Análise de Dados")
        self.setGeometry(100, 100, 1600, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(10, 5, 10, 5)
        connect_btn = QPushButton("Conectar")
        connect_btn.clicked.connect(self.show_connection_dialog)
        self.tema_btn = QPushButton("Modo Escuro")
        self.tema_btn.clicked.connect(self.alternar_tema)
        top_bar.addWidget(connect_btn)
        top_bar.addWidget(self.tema_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        
        nav_bar = QHBoxLayout()
        nav_bar.setContentsMargins(10, 5, 10, 5)
        
        self.gestao_btn = QPushButton("Gestão")
        self.gestao_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.gestao_btn.clicked.connect(lambda: self.switch_section("gestao"))
        
        self.analise_btn = QPushButton("Análise de Dados")
        self.analise_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.analise_btn.clicked.connect(lambda: self.switch_section("analise"))
        
        nav_bar.addWidget(self.gestao_btn)
        nav_bar.addWidget(self.analise_btn)
        nav_bar.addStretch()
        main_layout.addLayout(nav_bar)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.gestao_widget = GestaoWidget(self.db)
        self.analise_widget = AnaliseWidget(self.db)
        
        self.stacked_widget.addWidget(self.gestao_widget)
        self.stacked_widget.addWidget(self.analise_widget)
        
        self.switch_section("gestao")

    def switch_section(self, section):
        self.current_section = section
        
        self.gestao_btn.setStyleSheet("")
        self.analise_btn.setStyleSheet("")
        
        if section == "gestao":
            self.gestao_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            self.stacked_widget.setCurrentIndex(0)
        elif section == "analise":
            self.analise_btn.setStyleSheet("background-color: #2196F3; color: white;")
            self.stacked_widget.setCurrentIndex(1)

    def try_connect(self):
        if self.db.connect():
            QMessageBox.information(self, "Sucesso", "Conectado ao banco de dados!")
            self.load_data()
        else:
            QMessageBox.warning(self, "Erro", "Não foi possível conectar ao banco de dados.")

    def show_connection_dialog(self):
        dialog = ConnectionDialog(self)
        if dialog.exec():
            self.db.disconnect()
            self.db = Database(
                dbname=dialog.dbname_input.text(),
                user=dialog.user_input.text(),
                password=dialog.password_input.text(),
                host=dialog.host_input.text(),
                port=dialog.port_input.text()
            )
            if self.db.connect():
                QMessageBox.information(self, "Sucesso", "Conectado ao banco de dados!")
                self.gestao_widget.db = self.db
                self.analise_widget.db = self.db
                self.load_data()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível conectar ao banco de dados.")

    def load_data(self):
        if self.current_section == "gestao":
            self.gestao_widget.refresh_data()
        elif self.current_section == "analise":
            self.analise_widget.refresh_data()

    def alternar_tema(self):
        app = QApplication.instance()
        self.tema_claro = not self.tema_claro
        
        if self.tema_claro:
            aplicar_tema_claro(app)
            self.tema_btn.setText("Modo Escuro")
        else:
            aplicar_tema_escuro(app)
            self.tema_btn.setText("Modo Claro")
