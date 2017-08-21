from os import path
from PyQt5.QtCore import QCoreApplication, pyqtSlot
from PyQt5.QtWidgets import QWidget, QMenuBar, QFileDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QBoxLayout, QPlainTextEdit
from PyQt5.QtSvg import QSvgWidget
from lib import Converter
from lib.Dialog import Alert

class Window(QWidget):
    vars = dict()

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        menubar = QMenuBar(self)
        menu = menubar.addMenu("File")
        menu.addAction("Open", self.openFile)
        menu.addAction("Exit", QCoreApplication.instance().quit)

        appContainer = QBoxLayout(QBoxLayout.TopToBottom)

        self.preview = QSvgWidget()
        appContainer.addWidget(self.preview)
        self.varContainer = QGridLayout()
        appContainer.addLayout(self.varContainer)

        #TODO This is called variable for a reason
        self._addVar("@android:color/holo_blue_light", "#0000ff")
        self._addVar("@android:color/background_dark", "#ffffff")

        save = QPushButton("Convert")
        save.clicked.connect(self._saveConversion)
        appContainer.addWidget(save)

        container = QBoxLayout(QBoxLayout.LeftToRight, self)
        container.addLayout(appContainer)

        self.logs = QPlainTextEdit()
        self.logs.setReadOnly(True)
        container.addWidget(self.logs)

        self.setWindowTitle('AvdConverter')
        self.show()

    @pyqtSlot()
    def openFile(self):
        self.file, filter = QFileDialog.getOpenFileName(self, "Open image", "",
            "Vector graphics file (*.svg *.xml)")
        if self.file is None or self.file == '':
            return

        try:
            f = open(self.file, 'rb')
        except OSError as err:
            Alert(self, "Open failed", "{0}: open failed: {1}".format(path.relpath(self.file), err))
            self.file = None
            return

        self.previewContents = f.read()
        f.close()

        if self.file.endswith("xml"):
            self.previewContents, errs = Converter.avd2svg(self.previewContents)

        for e in errs:
            self.logs.appendPlainText(e)
        self._reloadPreview()

    def _addVar(self, var, val):
        varTxt = "@android:color/background_dark"
        self.varContainer.addWidget(QLabel(var), len(self.vars), 0)

        valEdit = QLineEdit(val)
        self.varContainer.addWidget(valEdit, len(self.vars), 1)

        self.vars[var] = valEdit

    def _reloadPreview(self):
        self.preview.load(self._replaceVarsSVG())

    def _saveConversion(self):
        fn = self.file[:-3]
        if self.file.endswith("svg"):
            fn += "xml"
        else:
            fn += "svg"

        if path.exists(fn):
            Alert(self, "Write failed", "{0}: exists, not erasing".format(path.relpath(fn)))
            return

        try:
            f = open(fn, 'wb')
        except OSError as err:
            Alert(self, "Write failed", "{0}: failed to open for writing: {1}".format(path.relpath(fn), err))
            return

        if fn.endswith("svg"):
            f.write(self._replaceVarsSVG())
        else:
            contents, errs = Converter.svg2avd(self.previewContents)
            for e in errs:
                self.logs.appendPlainText(e)
            f.write(contents)
        f.close()

    def _replaceVarsSVG(self):
        asset = self.previewContents
        for var, val in self.vars.items():
            asset = asset.replace(var.encode("utf-8"), val.text().encode("utf-8"))
        return asset
