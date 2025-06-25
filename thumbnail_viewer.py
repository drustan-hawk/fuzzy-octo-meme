import sys
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore


class ThumbnailViewer(QtWidgets.QWidget):
    """Widget that shows thumbnails for image files in a directory."""

    THUMBNAIL_SIZE = QtCore.QSize(128, 128)
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.setViewMode(QtWidgets.QListView.IconMode)
        self.list_widget.setIconSize(self.THUMBNAIL_SIZE)
        self.list_widget.setResizeMode(QtWidgets.QListView.Adjust)
        layout.addWidget(self.list_widget)

    def choose_folder(self) -> None:
        """Open a dialog to select a folder and populate thumbnails."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.populate_thumbnails(Path(folder))

    def populate_thumbnails(self, folder: Path) -> None:
        self.list_widget.clear()
        for file in sorted(folder.iterdir()):
            if file.suffix.lower() in self.IMAGE_EXTENSIONS:
                pixmap = QtGui.QPixmap(str(file))
                if not pixmap.isNull():
                    icon = QtGui.QIcon(
                        pixmap.scaled(
                            self.THUMBNAIL_SIZE,
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation,
                        )
                    )
                    item = QtWidgets.QListWidgetItem(icon, file.name)
                    self.list_widget.addItem(item)


class MainWindow(QtWidgets.QMainWindow):
    """Main window that hosts a :class:`ThumbnailViewer`."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Image Thumbnail Viewer")
        self.resize(800, 600)

        self.viewer = ThumbnailViewer(self)
        self.setCentralWidget(self.viewer)

        toolbar = self.addToolBar("File")
        open_action = QtGui.QAction("Open Folder", self)
        open_action.triggered.connect(self.viewer.choose_folder)
        toolbar.addAction(open_action)


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
