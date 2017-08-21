from PyQt5.QtWidgets import QMessageBox

def Alert(parent, title, message):
    dlg = QMessageBox(parent)
    dlg.setWindowTitle("Error")
    dlg.setText(message)
    dlg.show()
