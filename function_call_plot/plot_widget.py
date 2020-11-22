from typing import Optional

from PySide2.QtCore import QUrl, QDir
from PySide2.QtWebChannel import QWebChannel
from PySide2.QtWidgets import QWidget
from PySide2.QtWebEngineWidgets import QWebEngineView

from signal_hub import signalHub

class PlotWidget(QWebEngineView):

    def __init__(self, parent: Optional[QWidget]=...):
        super().__init__(parent)

        url = QUrl.fromLocalFile(QDir.currentPath() + '/resource/dist/index.html')
        self.channel = QWebChannel()
        self.channel.registerObject('signalHub', signalHub)
        self.page().setWebChannel(self.channel)
        self.load(url)
        self.show()
