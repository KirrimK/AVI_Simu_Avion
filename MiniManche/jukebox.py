"""Module qui s'occupera de lire les fichiers sons stockés dans le dossier data"""
from pygame import mixer
from time import sleep
from os import path

class Jukebox ():
    def __init__(self):
        mixer.init()
        self.PAOff = mixer.Sound (path.join(".","data","PAOff.wav"))
        self.overSpeed = mixer.Sound (path.join(".", "data", "overSpeed.wav"))
        self.tropBas = mixer.Sound (path.join(".","data","pullUp.wav"))
    def shutdownPA (self):
        self.PAOff.play()
    def overSpeeed (self):
        self.overSpeed.play()
    def pulllUp(self):
        self.tropBas.play()
