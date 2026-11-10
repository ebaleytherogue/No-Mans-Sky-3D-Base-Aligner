"""Portable desktop host for the existing Aligner viewer."""

import os
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QIODevice, QUrl
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import (
    QWebEnginePage, QWebEngineProfile, QWebEngineUrlRequestInterceptor,
    QWebEngineUrlRequestJob, QWebEngineUrlScheme, QWebEngineUrlSchemeHandler,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from nms_base_align_3d import AlignmentError, render_editor


VIEWER = QUrl("aligner://viewer/index.html")
BASE_FILTER = "NMSE base exports (*.nmsbase *.json);;All files (*)"


class ViewerRequests(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, request):
        url = request.requestUrl()
        if url != VIEWER and not url.toString().startswith("blob:aligner://viewer/"):
            request.block(True)


class ViewerContent(QWebEngineUrlSchemeHandler):
    def __init__(self, parent):
        super().__init__(parent)
        self.html = b"<!doctype html><title>NMS 3D Base Aligner</title>"

    def requestStarted(self, job):
        if job.requestUrl() != VIEWER:
            job.fail(QWebEngineUrlRequestJob.Error.RequestDenied)
            return
        buffer = QBuffer(job)
        buffer.setData(self.html)
        buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        job.reply(b"text/html", buffer)


class ViewerPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        return is_main_frame and url == VIEWER

    def createWindow(self, window_type):
        return None


class AlignerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NMS 3D Base Aligner")
        self.resize(1200, 800)
        self.profile = QWebEngineProfile(QApplication.instance())
        self.requests = ViewerRequests(self.profile)
        self.profile.setUrlRequestInterceptor(self.requests)
        self.content = ViewerContent(self.profile)
        self.profile.installUrlSchemeHandler(b"aligner", self.content)
        self.profile.downloadRequested.connect(self.save_export)

        self.view = QWebEngineView(self)
        self.view.setPage(ViewerPage(self.profile, self.view))
        self.setCentralWidget(self.view)
        self.view.load(VIEWER)

        menu = self.menuBar().addMenu("&File")
        for label, shortcut, callback in (
            ("Open &single base…", "Ctrl+O", lambda: self.open_base(False)),
            ("Open &Before and After…", "Ctrl+Shift+O", lambda: self.open_base(True)),
            ("&Save adjusted base…", "Ctrl+S", self.request_export),
        ):
            action = QAction(label, self)
            action.setShortcut(shortcut)
            action.triggered.connect(callback)
            menu.addAction(action)
        self.statusBar().showMessage("Use File to open one or two NMSE base exports.")

    def open_base(self, paired):
        before, _ = QFileDialog.getOpenFileName(self, "Open Before base", "", BASE_FILTER)
        if not before:
            return
        after = None
        if paired:
            after, _ = QFileDialog.getOpenFileName(
                self, "Open After base", str(Path(before).parent), BASE_FILTER
            )
            if not after:
                return
        try:
            html = render_editor(Path(before), Path(after) if after else None)
        except (AlignmentError, OSError, ValueError) as exc:
            QMessageBox.warning(self, "Cannot open base", str(exc))
            return
        self.content.html = html.encode("utf-8")
        self.view.reload()
        self.statusBar().showMessage(Path(before).name)

    def request_export(self):
        self.view.page().runJavaScript("document.getElementById('download')?.click()")

    def save_export(self, download):
        if download.url().scheme() != "blob" or download.downloadFileName() != "Adjusted Base.nmsbase":
            download.cancel()
            return
        destination, _ = QFileDialog.getSaveFileName(
            self, "Save adjusted base", "Adjusted Base.nmsbase", "NMSE base (*.nmsbase)"
        )
        if not destination:
            download.cancel()
            return
        path = Path(destination)
        download.setDownloadDirectory(str(path.absolute().parent))
        download.setDownloadFileName(path.name)
        download.accept()


def main():
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-background-networking --disable-component-update "
        "--disable-sync --no-pings --no-proxy-server "
        '--host-resolver-rules="MAP * ~NOTFOUND"'
    )
    scheme = QWebEngineUrlScheme(b"aligner")
    scheme.setSyntax(QWebEngineUrlScheme.Syntax.Host)
    QWebEngineUrlScheme.registerScheme(scheme)
    app = QApplication(sys.argv)
    window = AlignerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
