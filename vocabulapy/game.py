#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
VocabulaPy

Small python game where you translate words.

author: Daniel Monzonis
website: github.com/monzo94
"""

import os
from random import choice

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QMainWindow, qApp

from gui.gui import Ui_GameWindow


# Format filename for printing, ex. "basic_words.csv" to "Basic Words"
def formatFilename(filename):
    return filename[:filename.find('.')].replace('_', ' ').title()


class GameWindow(QMainWindow, Ui_GameWindow):

    def __init__(self, window, dictionaryManager):
        QMainWindow.__init__(self)
        Ui_GameWindow.__init__(self)
        self.setupUi(window)
        qApp.installEventFilter(self)
        self.dManager = dictionaryManager
        self.word = ""
        self.keyPressed = False
        self.gameRunning = False

        # Find all .csv files in the directory
        self.fileList = []
        for file in os.listdir(os.getcwd() + "/lists"):
            if file.endswith(".csv"):
                self.fileList.append(file)
        for filename in self.fileList:
            self.wordFileList.addItem(formatFilename(filename))

        self.playButton.clicked.connect(self.startGame)
        self.translateButton.clicked.connect(self.processWord)

    # Returns the selected languages in the menu's combo box ready to be
    # used for the Glosbe API
    def getLanguage(self):
        sourceList = ['en', 'es']
        destList = ['es', 'en']
        return (sourceList[self.sourceLangBox.currentIndex()],
                destList[self.destLangBox.currentIndex()])

    # Starts a new game. Loads the selected wordlist, building a new dictionary
    # if necessary, and sets up the settings
    def startGame(self):
        self.gameRunning = True
        self.dManager.load(
            "lists/" + self.fileList[self.wordFileList.currentRow()],
            *self.getLanguage()
        )
        self.wordReserve = list(self.dManager.dictionary.keys())
        self.endlessMode = self.endlessCheckBox.isChecked()
        self.correctCount = self.failCount = 0
        self.stack.setCurrentIndex(1)
        self.generateWord()

    # Maps return key press to processWord method
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and not self.keyPressed:
            if event.key() == Qt.Key_Return:
                self.keyPressed = True
                self.processWord()
        if event.type() == QEvent.KeyRelease and self.keyPressed:
            if event.key() == Qt.Key_Return:
                self.keyPressed = False
        return super(GameWindow, self).eventFilter(obj, event)

    # Grabs a new word from the word reserve and shows it on the game window,
    # or if the reserve is empty, finishes the game
    def generateWord(self):
        if self.wordReserve:
            self.word = choice(self.wordReserve)
            self.wordText.setText(self.word.title())
        else:
            self.lineEdit.setEnabled(False)
            self.feedbackText.setText("Finished!")
            self.gameRunning = False

    # Gets the input written on the line edit and processes it, comparing it
    # to possible solutions from the dictionary and determining if it was
    # correct or not, also updating the correct and incorrect counters, and
    # then generates a new word
    def processWord(self):
        if not self.gameRunning:
            return
        text = self.lineEdit.text()
        self.lineEdit.setText('')
        self.lineEdit.setFocus()
        if text in self.dManager.dictionary[self.word]:
            self.feedbackText.setText("Correct!")
            self.correctCount += 1
            self.okText.setText("""<html><head/><body><p>
                                <span style=" color:#07c327;">
                                OK: %s
                                </span></p></body></html>"""
                                % str(self.correctCount))
        else:
            self.feedbackText.setText("Incorrect...")
            self.failCount += 1
            self.failText.setText("""<html><head/><body><p>
                                  <span style=" color:#bf0808;">
                                  Fails: %s
                                  </span></p></body></html>"""
                                  % str(self.failCount))
        if not self.endlessMode and self.wordReserve:
            self.wordReserve.remove(self.word)
        self.generateWord()
