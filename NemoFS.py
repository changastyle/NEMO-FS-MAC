import sys, os, mimetypes
from PySide6.QtWidgets import (
    QApplication, QListView, QWidget, QVBoxLayout, QHBoxLayout,
    QFileSystemModel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QTextEdit, QSplitter
)
from PySide6.QtGui import QColor, QBrush, QPixmap
from PySide6.QtCore import QDir, QSize, Qt
from datetime import datetime

class MiniExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Explorador con Favoritos y Panel de Información")
        self.resize(1200, 600)

        self.history = []
        self.history_index = -1

        # Modelo de archivos
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.home = os.path.expanduser("~")
        self.model.setRootPath(self.home)

        # Vista principal de carpetas/archivos
        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(self.home))
        self.view.setViewMode(QListView.IconMode)
        self.view.setIconSize(QSize(64,64))
        self.view.setGridSize(QSize(120,110))
        self.view.setSpacing(10)
        self.view.doubleClicked.connect(self.enter_item)
        self.view.clicked.connect(self.show_info)

        # Barra de búsqueda + botón atrás
        self.path_bar = QLineEdit(self.home)
        self.path_bar.returnPressed.connect(self.navigate_to_path)
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.go_back)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_button)
        top_bar.addWidget(self.path_bar)

        # Barra lateral de favoritos
        self.fav_list = QListWidget()
        self.fav_list.setFixedWidth(200)
        self.fav_list.itemClicked.connect(self.favorite_clicked)
        self.favorites = []

        add_fav_btn = QPushButton("Agregar a Favoritos")
        add_fav_btn.clicked.connect(self.add_favorite)

        fav_layout = QVBoxLayout()
        fav_layout.addWidget(self.fav_list)
        fav_layout.addWidget(add_fav_btn)

        fav_panel = QWidget()
        fav_panel.setLayout(fav_layout)

        # Panel de información
        self.info_panel = QTextEdit()
        self.info_panel.setReadOnly(True)
        self.info_panel.setMinimumWidth(300)

        # Layout principal con splitter para redimensionar
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(fav_panel)
        splitter.addWidget(self.view)
        splitter.addWidget(self.info_panel)
        splitter.setSizes([200,600,300])

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_bar)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.push_history(self.home)

    # ------------------------------
    # Navegación
    # ------------------------------
    def enter_item(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.view.setRootIndex(self.model.index(path))
            self.path_bar.setText(path)
            self.push_history(path)
        else:
            self.show_info(index)  # mostrar info también para archivos

    def navigate_to_path(self):
        path = self.path_bar.text()
        if os.path.isdir(path):
            self.view.setRootIndex(self.model.index(path))
            self.push_history(path)

    def push_history(self, path):
        self.history = self.history[:self.history_index+1]
        self.history.append(path)
        self.history_index += 1

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.view.setRootIndex(self.model.index(path))
            self.path_bar.setText(path)

    # ------------------------------
    # Favoritos
    # ------------------------------
    def add_favorite(self):
        path = self.path_bar.text()
        if os.path.isdir(path) and path not in [f[0] for f in self.favorites]:
            color = QColor("orange")
            self.favorites.append((path,color))
            item = QListWidgetItem(os.path.basename(path))
            item.setData(1000,path)
            item.setForeground(QBrush(color))
            self.fav_list.addItem(item)

    def favorite_clicked(self, item):
        path = item.data(1000)
        if os.path.isdir(path):
            self.view.setRootIndex(self.model.index(path))
            self.path_bar.setText(path)
            self.push_history(path)

    # ------------------------------
    # Panel de información
    # ------------------------------
    def show_info(self, index):
        path = self.model.filePath(index)
        info_text = f"Ruta: {path}\n"
        if os.path.isdir(path):
            try:
                entries = os.listdir(path)
                folders = sum(os.path.isdir(os.path.join(path,e)) for e in entries)
                files = sum(os.path.isfile(os.path.join(path,e)) for e in entries)
                info_text += f"Tipo: Carpeta\nSubcarpetas: {folders}\nArchivos: {files}\n"
            except PermissionError:
                info_text += "Tipo: Carpeta\n(No se puede acceder al contenido)\n"
        else:
            size = os.path.getsize(path)
            ext = os.path.splitext(path)[1]
            created = datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d %H:%M:%S")
            modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
            info_text += f"Tipo: Archivo\nExtensión: {ext}\nTamaño: {size} bytes\nCreación: {created}\nModificación: {modified}\n"

            # Vista previa para imágenes
            mimetype,_ = mimetypes.guess_type(path)
            if mimetype and mimetype.startswith("image"):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaledToWidth(250, Qt.SmoothTransformation)
                    self.info_panel.clear()
                    self.info_panel.append(info_text)
                    self.info_panel.append("\nVista previa:")
                    self.info_panel.document().addResource(1, path, pixmap)
                    # Usamos HTML simple para mostrar
                    self.info_panel.append(f'<img src="{path}">')
                    return

        self.info_panel.setPlainText(info_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MiniExplorer()
    w.show()
    sys.exit(app.exec())
