
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

class SplashScreen(QSplashScreen):
    def __init__(self):
        pix = QPixmap(800, 500)
        super().__init__(pix)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(30)

    def on_timer(self):
        self.progress += 1
        self.showMessage(f"加载中... {self.progress}%", Qt.AlignBottom | Qt.AlignCenter)
        if self.progress >= 100:
            self.timer.stop()
            self.close()