from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


class WidgetBackend (QWidget):
    Axis0Signal = pyqtSignal (float) # axe de roulis
    Axis1Signal = pyqtSignal (float) # axe de tangage
    Axis2Signal = pyqtSignal (float) # boutons + et - -> pas utilisé
    Button0Signal = pyqtSignal (float) # gachette arrière -> pas utilisé
    Button1Signal = pyqtSignal (float) # gros bouton de gauche -> pas utilisé
    Button2Signal = pyqtSignal (float) # gros bouton de droite -> pas utilisé