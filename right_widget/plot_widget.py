from typing import Optional

from PySide2.QtCore import QUrl, QDir, Slot, Qt, QFileInfo
from PySide2.QtWebChannel import QWebChannel
from PySide2.QtWidgets import QWidget, QFileDialog
from PySide2.QtWebEngineWidgets import QWebEngineView

from signal_hub import signalHub

class PlotWidget(QWebEngineView):

    def __init__(self, parent: Optional[QWidget]=...):
        super().__init__(parent)

        self.setContextMenuPolicy(Qt.NoContextMenu)

        url = QUrl.fromLocalFile(QDir.currentPath() + '/resource/dist/index.html')
        self.channel = QWebChannel()
        self.channel.registerObject('signalHub', signalHub)
        self.page().setWebChannel(self.channel)
        self.page().profile().downloadRequested.connect(
            self.downloadPlotPngRequested)
        self.load(url)
        self.show()

        signalHub.dataFileOpened.connect(self.clearPlot)

    @Slot(object)
    def downloadPlotPngRequested(self, download_item):
        old_path = download_item.path()
        suffix = QFileInfo(old_path).suffix()
        path, _ = QFileDialog.getSaveFileName(self, "Save File", old_path, "*."+suffix)
        if path:
            download_item.setPath(path)
            download_item.accept()

    @Slot()
    def clearPlot(self):
        signalHub.funcCallDotProgress.emit('')
