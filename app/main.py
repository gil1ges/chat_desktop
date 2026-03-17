import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QStandardPaths, QUrl, Qt
from PySide6.QtGui import QColor, QIcon, QMouseEvent
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView

from .injected_style import INJECTED_STYLE


CHATGPT_URL = "https://chatgpt.com/"
BASE_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = BASE_DIR / "assets" / "chatgpt-icon.svg"
RESIZE_MARGIN = 10
PROFILE_NAME = "gpt-desktop"


class ChatPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        del level, line_number, source_id
        if "desktop-glass-style" in message:
            return
        print(message)


def create_web_profile(parent: QWidget) -> QWebEngineProfile:
    base_location = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    profile_root = Path(base_location) / PROFILE_NAME / "webengine"
    cache_path = profile_root / "cache"
    storage_path = profile_root / "storage"

    cache_path.mkdir(parents=True, exist_ok=True)
    storage_path.mkdir(parents=True, exist_ok=True)

    profile = QWebEngineProfile(PROFILE_NAME, parent)
    profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
    profile.setCachePath(str(cache_path))
    profile.setPersistentStoragePath(str(storage_path))
    return profile


class TitleBar(QFrame):
    def __init__(self, window: QWidget):
        super().__init__(window)
        self._window = window
        self._drag_start = QPoint()
        self.setObjectName("titleBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        title = QLabel("GPT Desktop")
        title.setObjectName("windowTitle")

        self.pin_button = QPushButton("Always on top")
        self.pin_button.setCheckable(True)
        self.pin_button.clicked.connect(self._toggle_on_top)

        self.min_button = QPushButton("—")
        self.min_button.clicked.connect(window.showMinimized)

        self.max_button = QPushButton("▢")
        self.max_button.clicked.connect(self._toggle_maximize)

        self.close_button = QPushButton("✕")
        self.close_button.clicked.connect(window.close)

        layout.addWidget(title)
        layout.addStretch(1)
        layout.addWidget(self.pin_button)
        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)

    def _toggle_on_top(self, checked: bool):
        flags = self._window.windowFlags()
        if checked:
            self._window.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self._window.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        self._window.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._window.isMaximized():
                return
            self._drag_start = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self._window.isMaximized():
                return
            self._window.move(event.globalPosition().toPoint() - self._drag_start)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._toggle_maximize()
            event.accept()

    def _toggle_maximize(self):
        if self._window.isMaximized():
            self._window.showNormal()
            self.max_button.setText("▢")
        else:
            self._window.showMaximized()
            self.max_button.setText("❐")


class GlassWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPT Desktop")
        self.setMinimumSize(720, 520)
        self.resize(1440, 920)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._resize_edges = Qt.Edge(0)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        self.title_bar = TitleBar(self)
        root.addWidget(self.title_bar)

        self.shell = QFrame()
        self.shell.setObjectName("shell")
        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)

        self.browser_host = BrowserHost()
        self.browser = self.browser_host.browser
        self.browser.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self._install_injected_script()
        self.browser.load(QUrl(CHATGPT_URL))
        shell_layout.addWidget(self.browser_host)

        root.addWidget(self.shell, 1)
        self.setStyleSheet(self._stylesheet())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and not self.isMaximized():
            edges = self._hit_test_edges(event.position().toPoint())
            if edges:
                window_handle = self.windowHandle()
                if window_handle is not None:
                    window_handle.startSystemResize(edges)
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.isMaximized():
            self.unsetCursor()
        else:
            edges = self._hit_test_edges(event.position().toPoint())
            self._update_cursor(edges)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)

    def changeEvent(self, event):
        if hasattr(self, "title_bar"):
            if self.isMaximized():
                self.title_bar.max_button.setText("❐")
            else:
                self.title_bar.max_button.setText("▢")
        super().changeEvent(event)

    def _hit_test_edges(self, pos: QPoint):
        rect = self.rect()
        edges = Qt.Edge(0)

        if pos.x() <= RESIZE_MARGIN:
            edges |= Qt.LeftEdge
        elif pos.x() >= rect.width() - RESIZE_MARGIN:
            edges |= Qt.RightEdge

        if pos.y() <= RESIZE_MARGIN:
            edges |= Qt.TopEdge
        elif pos.y() >= rect.height() - RESIZE_MARGIN:
            edges |= Qt.BottomEdge

        return edges

    def _update_cursor(self, edges):
        if edges in (Qt.LeftEdge, Qt.RightEdge):
            self.setCursor(Qt.SizeHorCursor)
        elif edges in (Qt.TopEdge, Qt.BottomEdge):
            self.setCursor(Qt.SizeVerCursor)
        elif edges in (Qt.TopEdge | Qt.LeftEdge, Qt.BottomEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeFDiagCursor)
        elif edges in (Qt.TopEdge | Qt.RightEdge, Qt.BottomEdge | Qt.LeftEdge):
            self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.unsetCursor()

    def _install_injected_script(self):
        script = QWebEngineScript()
        script.setName("desktop_glass_skin")
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setSourceCode(INJECTED_STYLE)
        self.browser.page().scripts().insert(script)

    def _stylesheet(self) -> str:
        return """
        QWidget {
            color: #f5f7fb;
            font-family: "Segoe UI", "Noto Sans", sans-serif;
            font-size: 14px;
            background: transparent;
        }

        QFrame#shell {
            background: rgba(10, 12, 16, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 24px;
        }

        QFrame#titleBar {
            background: rgba(10, 12, 16, 0.30);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 18px;
        }

        QLabel#windowTitle {
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 0.4px;
        }

        QPushButton {
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 12px;
            padding: 8px 14px;
        }

        QPushButton:hover {
            background: rgba(255, 255, 255, 0.16);
        }

        QPushButton:checked {
            background: rgba(113, 205, 255, 0.24);
            border-color: rgba(113, 205, 255, 0.42);
        }
        """


class BrowserHost(QFrame):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.profile = create_web_profile(self)
        self.browser = QWebEngineView(self)
        self.page = ChatPage(self.profile, self.browser)
        self.browser.setPage(self.page)
        layout.addWidget(self.browser)


def run():
    app = QApplication(sys.argv)
    app.setApplicationName("GPT Desktop")
    QGuiApplication.setDesktopFileName("gpt-desktop")
    app.setDesktopFileName("gpt-desktop")
    app.setWindowIcon(QIcon(str(ICON_PATH)))

    window = GlassWindow()
    window.setWindowIcon(QIcon(str(ICON_PATH)))
    window.show()

    sys.exit(app.exec())
