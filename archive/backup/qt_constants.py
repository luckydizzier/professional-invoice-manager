"""
Qt Constants Helper
Provides easy access to Qt constants
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidget, QHeaderView, QAbstractItemView

# Key constants
Key_Return = Qt.Key_Return
Key_Enter = Qt.Key_Enter
Key_Escape = Qt.Key_Escape
Key_Insert = Qt.Key_Insert
Key_Delete = Qt.Key_Delete
Key_Left = Qt.Key_Left
Key_Right = Qt.Key_Right
Key_Up = Qt.Key_Up
Key_Down = Qt.Key_Down
Key_F1 = Qt.Key_F1
Key_F5 = Qt.Key_F5
Key_F10 = Qt.Key_F10

# Dialog constants
DialogAccepted = QDialog.Accepted
DialogRejected = QDialog.Rejected

# Table constants
SelectRows = QAbstractItemView.SelectRows
SingleSelection = QAbstractItemView.SingleSelection
Stretch = QHeaderView.Stretch

# Item flags
ItemIsSelectable = Qt.ItemIsSelectable
ItemIsEnabled = Qt.ItemIsEnabled
