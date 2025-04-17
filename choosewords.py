from random import shuffle, sample

from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget, QPushButton
from qt.wordschoose import Ui_Form


class LearnWordChoose(QWidget, Ui_Form):
    def __init__(self, list_of_words):
        super().__init__()
        f = open('purple.stylesheet', 'r')
        self.styleData = f.read()
        f.close()
        self.setupUi(self)
        self.setStyleSheet(self.styleData)
        self.setWindowTitle("Учим слова!")
        self.words = list_of_words
        # добавляем слова в Qlabel
        if len(self.words) >= 5:
            self.shown = sample(self.words, 5)
        else:
            self.shown = self.words[:]
        for i in range(len(self.shown)):
            del self.words[self.words.index(self.shown[i])]
        if not bool(self.words):
            self.next.setText("Молодец!")
        self.next.setEnabled(False)
        self.original = list(map(lambda i: i[0], self.shown))
        shuffle(self.original)
        self.translation = list(map(lambda i: i[1], self.shown))
        shuffle(self.translation)
        self.push_orig = []
        self.push_trans = []
        for i in range(len(self.original)):
            temp = QPushButton(self.original[i])
            self.push_orig.append(temp)
            temp.clicked.connect(self.orig_selected)
            self.orig.addWidget(temp)
        for i in range(len(self.translation)):
            temp = QPushButton(self.translation[i])
            self.push_trans.append(temp)
            temp.clicked.connect(self.trans_selected)
            self.trans.addWidget(temp)
        # кнопка "Далее"
        self.next.clicked.connect(self.further)
        # выбранное "оригинальное" слово
        self.selected_original = ""
        # выбранное переведенное слово
        self.selected_translation = ""
        # таймер для гифки
        self.timer = QTimer()
        self.timer.timeout.connect(self.change)
        # подключение гифок
        self.great = QMovie("gif/happy.gif")
        self.great.setScaledSize(QSize(100, 100))
        self.bad = QMovie("gif/cry.gif")
        self.bad.setScaledSize(QSize(100, 100))
        self.check_all_solved = len(self.shown)

    def change(self):
        self.label.clear()
        self.timer.stop()

    def further(self):
        self.push_orig.clear()
        self.push_trans.clear()
        for i in reversed(range(self.orig.count())):
            self.orig.itemAt(i).widget().deleteLater()
        for i in reversed(range(self.trans.count())):
            self.trans.itemAt(i).widget().deleteLater()
        if len(self.words) >= 5:
            self.shown = sample(self.words, 5)
        else:
            self.shown = self.words[:]
        for i in range(len(self.shown)):
            del self.words[self.words.index(self.shown[i])]
        if not bool(self.words):
            self.next.setText("Молодец!")
        self.original = list(map(lambda i: i[0], self.shown))
        shuffle(self.original)
        self.translation = list(map(lambda i: i[1], self.shown))
        shuffle(self.translation)
        for i in range(len(self.original)):
            temp = QPushButton(self.original[i])
            self.push_orig.append(temp)
            temp.clicked.connect(self.orig_selected)
            self.orig.addWidget(temp)
        for i in range(len(self.translation)):
            temp = QPushButton(self.translation[i])
            self.push_trans.append(temp)
            temp.clicked.connect(self.trans_selected)
            self.trans.addWidget(temp)
        self.check_all_solved = len(self.shown)
        self.next.setEnabled(False)

    def orig_selected(self):
        self.selected_original = self.sender().text()
        if self.selected_translation == "":
            self.temp_mass = list(filter(lambda i: i[0] == self.selected_original, self.shown))
        else:
            correct_answer = False
            for i in self.temp_mass:
                if i[0] == self.selected_original and i[1] == self.selected_translation:
                    correct_answer = True
                    break
            if correct_answer:
                self.check_all_solved -= 1
                self.label.setMovie(self.great)
                self.great.start()
                self.sender().setEnabled(False)
                for i in self.push_trans:
                    if i.text() == self.selected_translation:
                        i.setEnabled(False)
                        break
            else:
                self.label.setMovie(self.bad)
                self.bad.start()
            self.timer.start(2000)
            self.selected_translation = ""
            self.selected_original = ""
            if self.check_all_solved == 0 and bool(self.words):
                self.next.setEnabled(True)

    def trans_selected(self):
        self.selected_translation = self.sender().text()
        if self.selected_original == "":
            self.temp_mass = list(filter(lambda i: i[1] == self.selected_translation, self.shown))
        else:
            correct_answer = False
            for i in self.temp_mass:
                if i[0] == self.selected_original and i[1] == self.selected_translation:
                    correct_answer = True
                    break
            if correct_answer:
                self.check_all_solved -= 1
                self.label.setMovie(self.great)
                self.great.start()
                self.sender().setEnabled(False)
                for i in self.push_orig:
                    if i.text() == self.selected_original:
                        i.setEnabled(False)
                        break
            else:
                self.label.setMovie(self.bad)
                self.bad.start()
            self.timer.start(2000)
            self.selected_translation = ""
            self.selected_original = ""
            if self.check_all_solved == 0 and bool(self.words):
                self.next.setEnabled(True)
