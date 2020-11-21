from typing import Optional

from PySide2.QtCore import QUrl, QDir
from PySide2.QtWidgets import QWidget
from PySide2.QtWebEngineWidgets import QWebEngineView


class PlotWidget(QWebEngineView):

    def __init__(self, parent: Optional[QWidget]=...):
        super().__init__(parent)

        url = QUrl.fromLocalFile(QDir.currentPath() + '/resource/html/index.html')
        self.load(url)
        self.show()
