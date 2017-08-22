# Copyright 2017 Cédric Legrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from os import path
from PyQt5.QtCore import QCoreApplication, QDir, QModelIndex, pyqtSlot
from PyQt5.QtWidgets import (QBoxLayout, QFileDialog, QFileSystemModel, QGridLayout, QLabel,
    QLineEdit, QMenuBar, QMessageBox, QPlainTextEdit, QPushButton, QTreeView, QWidget)
from PyQt5.QtSvg import QSvgWidget
from lib import Converter

class Window(QWidget):
    vars = dict()

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        menubar = QMenuBar(self)
        menu = menubar.addMenu("File")
        menu.addAction("Exit", QCoreApplication.instance().quit)

        container = QBoxLayout(QBoxLayout.LeftToRight, self)
        self._initDirUI(container)
        self._initAppUI(container)

        self.logs = QPlainTextEdit()
        self.logs.setReadOnly(True)
        container.addWidget(self.logs)

        self.setWindowTitle('AvdConverter')
        self.show()

    def _initDirUI(self, container):
        dirContainer = QBoxLayout(QBoxLayout.TopToBottom)

        self.model = QFileSystemModel()
        self.model.setNameFilters(["*.svg", "*.xml"])
        self.model.setNameFilterDisables(False)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.activated.connect(self._fileSelected)
        self._setRoot(QDir.currentPath())
        dirContainer.addWidget(self.tree)

        changeDirButton = QPushButton("Select directory")
        changeDirButton.clicked.connect(self._changeDir)
        dirContainer.addWidget(changeDirButton)
        container.addLayout(dirContainer)

    def _initAppUI(self, container):
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

        container.addLayout(appContainer)


    def _changeDir(self):
        dir = QFileDialog.getExistingDirectory(self, "Work directory", ".")
        if dir is not None and dir != '':
            self._setRoot(dir)

    def _setRoot(self, path):
        self.model.setRootPath(path)
        self.tree.setRootIndex(self.model.index(path))

    @pyqtSlot(QModelIndex)
    def _fileSelected(self, idx):
        fn = self.model.filePath(idx)
        if path.isfile(fn):
            self.openFile(fn)


    @pyqtSlot()
    def openFile(self, fn):
        if not path.isfile(fn) or not (fn.endswith(".xml") or fn.endswith(".svg")):
            QMessageBox.critical(self, "Open failed",
                "{0}: not a valid file".format(path.relpath(fn)))
            return

        try:
            f = open(fn, 'rb')
        except OSError as err:
            QMessageBox.critical(self, "Open failed",
                "{0}: open failed: {1}".format(path.relpath(fn), err))
            return

        self.previewContents = f.read()
        f.close()

        self.file = fn
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
            answer = QMessageBox.question(self, "File exists",
                "{0} already exists, would you like to override it?".format(path.relpath(fn)))
            if answer == QMessageBox.No:
                return

        try:
            f = open(fn, 'wb')
        except OSError as err:
            QMessageBox.critical(self, "Write failed",
                "{0}: failed to open for writing: {1}".format(path.relpath(fn), err))
            return

        if fn.endswith("svg"):
            f.write(self._replaceVarsSVG())
        else:
            contents, errs = Converter.svg2avd(self._replaceVarsAVD())
            for e in errs:
                self.logs.appendPlainText(e)
            f.write(contents)
        f.close()

    def _replaceVarsSVG(self):
        asset = self.previewContents
        for var, val in self.vars.items():
            asset = asset.replace(var.encode("utf-8"), val.text().encode("utf-8"))
        return asset

    def _replaceVarsAVD(self):
        asset = self.previewContents
        for var, val in self.vars.items():
            asset = asset.replace(val.text().encode("utf-8"), var.encode("utf-8"))
        return asset
