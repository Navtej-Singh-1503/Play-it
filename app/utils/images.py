import requests
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QObject, Signal
from PySide6.QtGui import QPixmap

class ImageLoader(QObject):
    loaded = Signal(str, QPixmap)
    def load(self, url, key):
        try:
            data = requests.get(url, timeout=8).content
            pix = QPixmap(); pix.loadFromData(QByteArray(data)); self.loaded.emit(key, pix)
        except Exception: pass
