import sys, os
from PySide6.QtWidgets import (
    QApplication, QListView, QWidget, QVBoxLayout,
    QFileSystemModel, QLineEdit, QHBoxLayout
)
from PySide6.QtCore import QDir, QSize


class FileExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Explorador")
        self.resize(900, 600)

        # Modelo de archivos
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)  # solo carpetas

        self.home = os.path.expanduser("~")
        self.model.setRootPath(self.home)

        # Vista de iconos
        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(self.home))
        self.view.setViewMode(QListView.IconMode)
        self.view.setIconSize(QSize(64, 64))
        self.view.setGridSize(QSize(120, 110))
        self.view.setSpacing(10)
        self.view.doubleClicked.connect(self.enter_folder)

        # Barra de navegación (breadcrumbs simple)
        self.path_bar = QLineEdit(self.home)
        self.path_bar.returnPressed.connect(self.navigate_to_path)

        # Layout
        top = QHBoxLayout()
        top.addWidget(self.path_bar)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def enter_folder(self, index):
        """Navegar al hacer doble click en carpeta"""
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.view.setRootIndex(self.model.index(path))
            self.path_bar.setText(path)

    def navigate_to_path(self):
        """Navegar cuando el usuario escribe una ruta"""
        path = self.path_bar.text()
        if os.path.isdir(path):
            self.view.setRootIndex(self.model.index(path))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FileExplorer()
    w.show()
    sys.exit(app.exec())
