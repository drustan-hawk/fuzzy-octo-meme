import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from PySide6 import QtCore, QtGui, QtWidgets


@dataclass
class ImageItem:
    """Model item holding an image path and optional tags."""

    path: Path
    tags: set[str] = field(default_factory=set)


class ImageListModel(QtCore.QAbstractListModel):
    """List model that stores :class:`ImageItem` instances."""

    def __init__(self, items: Iterable[ImageItem] | None = None, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._items: list[ImageItem] = list(items) if items else []

    def rowCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self._items)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not (0 <= index.row() < len(self._items)):
            return None

        item = self._items[index.row()]

        if role == QtCore.Qt.DisplayRole:
            return item.path.name
        if role == QtCore.Qt.DecorationRole:
            pixmap = QtGui.QPixmap(str(item.path))
            if pixmap.isNull():
                return None
            return pixmap.scaled(
                ThumbnailViewer.THUMBNAIL_SIZE,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        if role == QtCore.Qt.UserRole:
            return item
        return None

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:  # type: ignore[override]
        flags = super().flags(index)
        return flags | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def set_images(self, paths: Iterable[Path]) -> None:
        """Replace model items with the given image paths."""

        self.beginResetModel()
        self._items = [ImageItem(path=path) for path in paths]
        self.endResetModel()

    def image_at(self, row: int) -> ImageItem:
        return self._items[row]


class ThumbnailDelegate(QtWidgets.QStyledItemDelegate):
    """Delegate to display thumbnails with overlaid file paths."""

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        pixmap = index.data(QtCore.Qt.DecorationRole)
        if not isinstance(pixmap, QtGui.QPixmap):
            super().paint(painter, option, index)
            return

        painter.save()

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        # Center the pixmap within the available rect
        pixmap_rect = pixmap.rect()
        pixmap_rect.moveCenter(option.rect.center())
        painter.drawPixmap(pixmap_rect.topLeft(), pixmap)


        # Draw a semi-transparent text background at the bottom
        text = str(index.data(QtCore.Qt.DisplayRole))
        metrics = QtGui.QFontMetrics(painter.font())
        text_height = metrics.lineSpacing() + 4
        text_rect = QtCore.QRect(
            pixmap_rect.left(),
            pixmap_rect.bottom() - text_height + 1,
            pixmap_rect.width(),
            text_height,
        )
        # text_rect = text_rect.marginsRemoved(QtCore.QMargins(2, 2, 2, 2))

        bg_color = option.palette.window().color()
        bg_color.setAlpha(160)
        painter.fillRect(text_rect, bg_color)

        elided = metrics.elidedText(text, QtCore.Qt.ElideRight, text_rect.width())
        painter.setPen(option.palette.windowText().color())
        painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, elided)

        painter.restore()



class ThumbnailViewer(QtWidgets.QWidget):
    """Widget that shows thumbnails for image files in a directory."""

    THUMBNAIL_SIZE = QtCore.QSize(128, 128)
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        self.model = ImageListModel(parent=self)
        self.list_view = QtWidgets.QListView(self)
        self.list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.list_view.setIconSize(self.THUMBNAIL_SIZE)
        self.list_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view.setModel(self.model)
        self.list_view.setItemDelegate(ThumbnailDelegate(self.list_view))
        layout.addWidget(self.list_view)

    def choose_folder(self) -> None:
        """Open a dialog to select a folder and populate thumbnails."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.populate_thumbnails(Path(folder))

    def populate_thumbnails(self, folder: Path) -> None:
        paths: list[Path] = []
        for file in sorted(folder.iterdir()):
            if file.suffix.lower() in self.IMAGE_EXTENSIONS:
                paths.append(file)

        self.model.set_images(paths)


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
