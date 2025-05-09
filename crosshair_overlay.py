import sys
import os
import json
import threading
import ctypes
import keyboard
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QColor, QPixmap, QFontDatabase, QFont
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QColorDialog, QAction

class CrosshairOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.settings_path = "settings.json"
        self.settings = self.load_settings()
        self.crosshair_visible = self.settings.get("visible", True)
        self.crosshair_style = self.settings.get("style", "cross")
        self.pulse_phase = 0
        self.styles = ["cross", "dot", "cross_dot", "circle", "circle_dot"]

        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        self.screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(self.screen_geometry)

        self.setup_hotkeys()
        self.setup_tray_icon()

        self.set_click_through()
        self.settings_watcher_thread = threading.Thread(target=self.watch_settings_file, daemon=True)
        self.settings_watcher_thread.start()

        self.pulse_timer = QtCore.QTimer()
        self.pulse_timer.timeout.connect(self.animate_pulse)
        self.pulse_timer.start(50)

    def load_settings(self):
        default_settings = {
            "color": "red",
            "thickness": 2,
            "size": 25,
            "style": "cross",
            "visible": True
        }
        try:
            with open(self.settings_path, "r") as f:
                return {**default_settings, **json.load(f)}
        except Exception:
            return default_settings

    def save_settings(self):
        self.settings["style"] = self.crosshair_style
        self.settings["visible"] = self.crosshair_visible
        with open(self.settings_path, "w") as f:
            json.dump(self.settings, f, indent=2)

    def watch_settings_file(self):
        last_mtime = os.path.getmtime(self.settings_path) if os.path.exists(self.settings_path) else 0
        while True:
            try:
                current_mtime = os.path.getmtime(self.settings_path)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    self.settings = self.load_settings()
                    self.crosshair_style = self.settings.get("style", self.crosshair_style)
                    self.repaint()
            except Exception:
                pass
            time.sleep(1)

    def set_click_through(self):
        hwnd = self.winId().__int__()
        extended_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, extended_style | 0x80000 | 0x20)

    def animate_pulse(self):
        if self.crosshair_style in ("dot", "circle", "circle_dot", "cross_dot"):
            self.pulse_phase = (self.pulse_phase + 1) % 20
            self.repaint()

    def paintEvent(self, event):
        if not self.crosshair_visible:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        color = QtGui.QColor(self.settings.get("color", "red"))
        painter.setPen(QtGui.QPen(color, self.settings.get("thickness", 2)))

        w = self.screen_geometry.width()
        h = self.screen_geometry.height()
        center = QtCore.QPoint(w // 2, h // 2)
        size = self.settings.get("size", 25)

        style = self.crosshair_style
        pulse_size = 2 + abs(10 - self.pulse_phase) // 2

        if style in ("cross", "cross_dot"):
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
        if style in ("dot", "cross_dot", "circle_dot"):
            painter.setBrush(color)
            painter.drawEllipse(center, pulse_size, pulse_size)
        if style in ("circle", "circle_dot"):
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawEllipse(center, size, size)

    def setup_hotkeys(self):
        threading.Thread(target=self.register_hotkeys, daemon=True).start()

    def register_hotkeys(self):
        keyboard.add_hotkey("F8", self.toggle_visibility)
        keyboard.add_hotkey("shift+F8", QtWidgets.qApp.quit)
        keyboard.add_hotkey("page up", self.next_style)
        keyboard.add_hotkey("page down", self.prev_style)
        keyboard.wait()

    def next_style(self):
        idx = self.styles.index(self.crosshair_style)
        self.crosshair_style = self.styles[(idx + 1) % len(self.styles)]
        self.save_settings()
        self.repaint()

    def prev_style(self):
        idx = self.styles.index(self.crosshair_style)
        self.crosshair_style = self.styles[(idx - 1) % len(self.styles)]
        self.save_settings()
        self.repaint()

    def setup_tray_icon(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "icon.ico")

        self.tray_icon = QSystemTrayIcon(QIcon(icon_path if os.path.exists(icon_path) else None))
        self.tray_icon.setToolTip("Crosshair Overlay")

        tray_menu = QMenu()

        style_menu = tray_menu.addMenu("Style")
        for style in self.styles:
            icon = self.generate_style_icon(style)
            action = QAction(icon, style.replace("_", "+").capitalize(), self)
            action.triggered.connect(lambda checked, s=style: self.set_style(s))
            style_menu.addAction(action)

        self.color_action = tray_menu.addAction("Change Color")
        self.color_action.triggered.connect(self.pick_color)

        self.toggle_action = tray_menu.addAction("Show/Hide Crosshair")
        self.toggle_action.triggered.connect(self.toggle_visibility)

        tray_menu.addSeparator()

        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(QtWidgets.qApp.quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setVisible(True)
        self.color_action.setEnabled(self.crosshair_visible)

    def generate_style_icon(self, style):
        pixmap = QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QColor(self.settings.get("color", "red")), 2))
        center = QtCore.QPoint(16, 16)
        size = 10

        if style in ("cross", "cross_dot"):
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
        if style in ("dot", "cross_dot", "circle_dot"):
            painter.setBrush(QColor(self.settings.get("color", "red")))
            painter.drawEllipse(center, 2, 2)
        if style in ("circle", "circle_dot"):
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawEllipse(center, size, size)
        painter.end()
        return QIcon(pixmap)

    def pick_color(self):
        if not self.crosshair_visible:
            return
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings["color"] = color.name()
            self.save_settings()
            self.repaint()

    def toggle_visibility(self):
        self.crosshair_visible = not self.crosshair_visible
        self.color_action.setEnabled(self.crosshair_visible)
        self.save_settings()

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        icon_file = "icon-hidden.ico" if not self.crosshair_visible else "icon.ico"
        icon_path = os.path.join(base_path, icon_file)

        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))

        self.repaint()

    def set_style(self, style):
        self.crosshair_style = style
        self.settings["style"] = style
        self.save_settings()
        self.repaint()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    overlay = CrosshairOverlay()
    overlay.showFullScreen()
    sys.exit(app.exec_())
