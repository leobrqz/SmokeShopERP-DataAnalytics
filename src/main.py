import sys
from PyQt6.QtWidgets import QApplication
from interface import MainWindow, aplicar_tema_claro

if __name__ == "__main__":
    app = QApplication(sys.argv)
    aplicar_tema_claro(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

