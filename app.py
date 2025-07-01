import sys, os, shutil, hashlib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileSystemModel, QTreeView, QListWidget, QListWidgetItem,
                             QSplitter, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QMessageBox, QLineEdit)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QModelIndex, QDir
from PIL import Image
import imagehash
import cv2

SUPPORTED_IMAGE_EXT = ['.jpg', '.jpeg', '.png']
SUPPORTED_VIDEO_EXT = ['.mp4', '.mov', '.avi']
RECYCLE_BIN = ".recycle_bin"

class MediaManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Media Manager")
        self.setGeometry(100, 100, 1200, 700)
        self.dark_mode = True

        splitter = QSplitter(self)
        self.setCentralWidget(splitter)

        # Folder Tree
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(QDir.rootPath())
        self.dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.AllEntries)
        self.tree = QTreeView()
        self.tree.setModel(self.dir_model)
        self.tree.setRootIndex(self.dir_model.index(QDir.rootPath()))
        self.tree.clicked.connect(self.on_folder_selected)
        self.tree.doubleClicked.connect(self.on_folder_double_clicked)
        splitter.addWidget(self.tree)

        # Media List Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search media...")
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.search_files)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        right_layout.addLayout(search_layout)

        self.media_list = QListWidget()
        self.media_list.setIconSize(QSize(128, 128))
        self.media_list.itemDoubleClicked.connect(self.open_media)
        right_layout.addWidget(self.media_list)

        btn_bar = QHBoxLayout()
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_undo = QPushButton("Undo Last Delete")
        self.btn_undo.clicked.connect(self.undo_delete)
        self.btn_back = QPushButton("Back")
        self.btn_back.clicked.connect(self.go_back)
        btn_bar.addWidget(self.btn_delete)
        btn_bar.addWidget(self.btn_undo)
        btn_bar.addWidget(self.btn_back)
        right_layout.addLayout(btn_bar)

        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)

        if not os.path.exists(RECYCLE_BIN):
            os.makedirs(RECYCLE_BIN)

        self.last_deleted = []
        self.previous_indexes = []
        self.current_folder = QDir.rootPath()
        self.apply_dark_theme()

    def on_folder_selected(self, index):
        folder_path = self.dir_model.filePath(index)
        if os.path.isdir(folder_path):
            self.current_folder = folder_path
            self.populate_media_list(folder_path)

    def on_folder_double_clicked(self, index: QModelIndex):
        folder_path = self.dir_model.filePath(index)
        if os.path.isdir(folder_path):
            self.previous_indexes.append(self.tree.rootIndex())
            self.tree.setRootIndex(index)
            self.current_folder = folder_path
            self.populate_media_list(folder_path)

    def go_back(self):
        if self.previous_indexes:
            prev_index = self.previous_indexes.pop()
            folder_path = self.dir_model.filePath(prev_index)
            self.tree.setRootIndex(prev_index)
            self.current_folder = folder_path
            self.populate_media_list(folder_path)

    def populate_media_list(self, folder):
        self.media_list.clear()
        self.media_files = []

        for filename in os.listdir(folder):
            full_path = os.path.join(folder, filename)
            if not os.path.isfile(full_path) or os.path.islink(full_path):
                continue

            ext = os.path.splitext(filename)[1].lower()
            if ext in SUPPORTED_IMAGE_EXT + SUPPORTED_VIDEO_EXT:
                item = QListWidgetItem()
                item.setText(filename)
                item.setToolTip(full_path)
                item.setData(Qt.UserRole, full_path)

                if ext in SUPPORTED_IMAGE_EXT:
                    pixmap = QPixmap(full_path)
                    if not pixmap.isNull():
                        item.setIcon(QIcon(pixmap.scaled(128, 128, Qt.KeepAspectRatio)))

                elif ext in SUPPORTED_VIDEO_EXT:
                    cap = cv2.VideoCapture(full_path)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            thumbnail_path = full_path + '_thumb.jpg'
                            cv2.imwrite(thumbnail_path, frame)
                            pixmap = QPixmap(thumbnail_path)
                            if not pixmap.isNull():
                                item.setIcon(QIcon(pixmap.scaled(128, 128, Qt.KeepAspectRatio)))
                            os.remove(thumbnail_path)
                        cap.release()

                self.media_list.addItem(item)
                self.media_files.append(full_path)

    def search_files(self):
        query = self.search_input.text().lower()
        if not query:
            self.populate_media_list(self.current_folder)
            return

        self.media_list.clear()
        for path in self.media_files:
            if query in os.path.basename(path).lower():
                item = QListWidgetItem()
                item.setText(os.path.basename(path))
                item.setToolTip(path)
                item.setData(Qt.UserRole, path)
                ext = os.path.splitext(path)[1].lower()

                if ext in SUPPORTED_IMAGE_EXT:
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        item.setIcon(QIcon(pixmap.scaled(128, 128, Qt.KeepAspectRatio)))
                elif ext in SUPPORTED_VIDEO_EXT:
                    cap = cv2.VideoCapture(path)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            thumbnail_path = path + '_thumb.jpg'
                            cv2.imwrite(thumbnail_path, frame)
                            pixmap = QPixmap(thumbnail_path)
                            if not pixmap.isNull():
                                item.setIcon(QIcon(pixmap.scaled(128, 128, Qt.KeepAspectRatio)))
                            os.remove(thumbnail_path)
                        cap.release()

                self.media_list.addItem(item)

    def open_media(self, item):
        path = item.data(Qt.UserRole)
        os.startfile(path) if os.name == 'nt' else os.system(f'xdg-open "{path}"')

    def delete_selected(self):
        selected = self.media_list.selectedItems()
        if not selected:
            return
        for item in selected:
            path = item.data(Qt.UserRole)
            filename = os.path.basename(path)
            dest = os.path.join(RECYCLE_BIN, filename)
            shutil.move(path, dest)
            self.last_deleted.append((path, dest))
            self.media_list.takeItem(self.media_list.row(item))

    def undo_delete(self):
        for original, deleted in self.last_deleted:
            shutil.move(deleted, original)
        self.last_deleted.clear()
        QMessageBox.information(self, "Undo", "Restored deleted files.")

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2d2d2d; color: white; }
            QPushButton { background-color: #444; color: white; padding: 5px; }
            QListWidget { background-color: #1e1e1e; color: white; }
            QTreeView { background-color: #1e1e1e; color: white; }
            QLineEdit { background-color: #333; color: white; padding: 4px; }
        """)

    def find_duplicates(self):
        hashes = {}
        duplicates = []
        for path in self.media_files:
            ext = os.path.splitext(path)[1].lower()
            if ext in SUPPORTED_IMAGE_EXT:
                h = str(imagehash.average_hash(Image.open(path)))
                if h in hashes:
                    duplicates.append((hashes[h], path))
                else:
                    hashes[h] = path
        return duplicates

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MediaManager()
    window.show()
    sys.exit(app.exec_())
