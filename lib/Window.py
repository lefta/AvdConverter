from os import path
from PyQt5.QtCore import QCoreApplication, pyqtSlot
from PyQt5.QtWidgets import QWidget, QMenuBar, QFileDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QBoxLayout
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

        container = QBoxLayout(QBoxLayout.TopToBottom, self)

        self.preview = QSvgWidget()
        container.addWidget(self.preview)
        self.varContainer = QGridLayout()
        container.addLayout(self.varContainer)

        #TODO This is called variable for a reason
        self._addVar("@android:color/holo_blue_light", "#0000ff")
        self._addVar("@android:color/background_dark", "#ffffff")

        buttonContainer = QBoxLayout(QBoxLayout.LeftToRight)
        save = QPushButton("Convert")
        save.clicked.connect(self._saveConversion)
        container.addWidget(save)

        self.setWindowTitle('AvdConverter')
        self.show()

    @pyqtSlot()
    def openFile(self):
        self.file, filter = QFileDialog.getOpenFileName(self, "Open image", "",
            "Vector graphics file (*.svg *.xml)")
        if self.file is None:
            return

        try:
            f = open(self.file, 'r')
        except OSError as err:
            Alert(self, "Open failed", "{0}: open failed: {1}".format(path.relpath(self.file), err))
            self.file = None

        asset = f.read().encode("utf-8")
        f.close()

        if self.file.endswith("xml"):
            asset = Converter.avd2svg(asset)

        self.previewContents = asset
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
            f = open(fn, 'w')
        except OSError as err:
            Alert(self, "Write failed", "{0}: failed to open for writing: {1}".format(path.relpath(fn), err))
            return

        if fn.endswith("svg"):
            f.write(self._replaceVarsSVG().decode("utf-8"))
        else:
            f.write(Converter.svg2avd(self.previewContents).decode("utf-8"))
        f.close()

    def _replaceVarsSVG(self):
        asset = self.previewContents
        for var, val in self.vars.items():
            asset = asset.replace(var.encode("utf-8"), val.text().encode("utf-8"))
        return asset
