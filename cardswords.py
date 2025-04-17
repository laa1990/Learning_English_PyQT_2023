from random import shuffle

from PyQt5.QtWidgets import QWidget
from qt.wordscards import Ui_Form


class LearnWordsCards(QWidget, Ui_Form):
    def __init__(self, list_of_words):
        super().__init__()
        f = open('purple.stylesheet', 'r')
        self.styleData = f.read()
        f.close()
        self.setupUi(self)
        self.setStyleSheet(self.styleData)
        self.setWindowTitle("Учим слова!")
        self.words = list_of_words
        shuffle(self.words)
        self.current_word = 0
        self.current_translate = 0
        self.card.clicked.connect(self.change)
        self.back.clicked.connect(self.left)
        self.forward.clicked.connect(self.right)
        self.orig_trans.setText(self.words[0][0])
        self.back.setEnabled(False)
        if len(self.words) == 1:
            self.forward.setEnabled(False)

    def change(self):
        if self.current_translate == 0:
            self.current_translate = 1
        else:
            self.current_translate = 0
        self.orig_trans.setText(self.words
                                [self.current_word][self.current_translate])

    def left(self):
        if self.current_word == 1:
            self.back.setEnabled(False)
        self.current_translate = 0
        self.current_word -= 1
        if not self.forward.isEnabled():
            if len(self.words) > 1:
                self.forward.setEnabled(True)
        self.orig_trans.setText(self.words[self.current_word][self.current_translate])

    def right(self):
        if self.current_word == len(self.words) - 2:
            self.forward.setEnabled(False)
        self.current_translate = 0
        self.current_word += 1
        if not self.back.isEnabled():
            if len(self.words) > 1:
                self.back.setEnabled(True)
        self.orig_trans.setText(self.words[self.current_word][self.current_translate])
