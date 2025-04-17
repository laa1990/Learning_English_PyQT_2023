import csv
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QHeaderView, QPushButton, \
    QVBoxLayout, QSpacerItem, QSizePolicy, QTableWidgetItem, \
    QFileDialog, QInputDialog, QDialog
from PyQt5.QtCore import Qt
import sqlite3
from string import ascii_letters
from choosewords import LearnWordChoose
from addmodule import AddNewModule
from cardswords import LearnWordsCards
from qt.project import Ui_MainWindow

# классы ошибок для работы с регистрацией


class UserExistsError(Exception):
    pass


class WrongPasswordError(Exception):
    pass


class WrongNameError(Exception):
    pass


class ZeroNamePassError(Exception):
    pass


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # прогружаем дизайн
        f = open('purple.stylesheet', 'r')
        self.styleData = f.read()
        f.close()
        self.setupUi(self)
        self.setStyleSheet(self.styleData)
        self.setWindowTitle("Английский")

        # по умолчанию регистрация не пройдена
        self.registration = False
        # пока нет входа в аккаунт, кнопки не показываются
        self.setFixedSize(600, 520)
        # по умолчанию страница с регистрацией
        self.stackedWidget.setCurrentIndex(0)
        self.reg_pass_btn.clicked.connect(self.reg_pass)
        # подключение к БД
        self.con = sqlite3.connect("database.db")
        self.cur = self.con.cursor()
        self.registration_label.setWordWrap(True)
        # логина и пароля еще нет
        self.login = ""
        self.password = ""
        # прячем кнопки "изменить пароль" и "показать пароль"
        self.show_hide_pass_btn.hide()
        self.change_pass_btn.hide()
        self.add_image.hide()
        self.image.hide()
        # кнопки "Личный кабинет", "Карточки" и "Справка"
        self.start_btn.clicked.connect(self.changeMainPage)
        self.cards_btn.clicked.connect(self.changeMainPage)
        self.info_btn.clicked.connect(self.changeMainPage)
        # показать и скрыть пароль
        self.show_hide_pass_btn.clicked.connect(self.show_hide_password)
        # изменить пароль
        self.change_pass_btn.clicked.connect(self.change_pass)
        # добавить модуль
        self.add_modul_btn.clicked.connect(self.add_module)
        self.add_words_btn.clicked.connect(self.add_module)
        # выбрать картинку для аватара
        self.add_image.clicked.connect(self.choose_photo)
        # модули в разделе "карточки"
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        # учить слова
        self.learn_modul_btn.clicked.connect(self.choose_method)
        self.learnAll_btn.clicked.connect(self.choose_method)
        # импорт в csv
        self.csv_btn.clicked.connect(self.importing)

    # конвертируем изображение в бинарный вид
    def covert_file_to_binary(self, filename):
        with open(filename, mode="rb") as file:
            data = sqlite3.Binary(file.read())
        return data

    # выбираем аватар из файлов
    def choose_photo(self):
        try:
            filename = QFileDialog.getOpenFileName(
                self, 'Выбрать картинку', '',
                'Картинка (*.jpg);;Картинка (*.png)')[0]
            data = self.covert_file_to_binary(filename)
            updating = "UPDATE users SET image = ? WHERE name = ?"
            self.cur.execute(updating, (data, self.login))
            self.con.commit()
            self.add_image.setText("Изменить аватар")
            with open("tempfile.jpg", "wb") as f:
                f.write(data)
            self.pixmap = QPixmap("tempfile.jpg")
            self.pixmap = self.pixmap.scaled(130, 130, Qt.KeepAspectRatio)
            self.image.setPixmap(self.pixmap)
            self.image.show()
        except Exception:
            pass

    # вход в аккаунт или регистрация нового пользователя
    def reg_pass(self):
        try:
            # если входа в аккаунт не было
            if not self.registration:
                # если хотя бы одно поле пусто
                if self.user_name.text() == "" or self.user_password == "":
                    raise ZeroNamePassError
                # если в имени неккоректные символы
                if not all(map(lambda i: i in ascii_letters or i.isdigit() or
                               i == "_", self.user_name.text())) or \
                        len(self.user_name.text()) < 5 or \
                        len(self.user_name.text()) > 16:
                    raise WrongNameError
                # если в пароле неккоректные символы
                if not all(map(lambda i: i in ascii_letters or i.isdigit() or
                               i == "_", self.user_password.text())) or \
                        len(self.user_password.text()) < 5 or \
                        len(self.user_password.text()) > 16:
                    raise WrongPasswordError
                checker_name = "SELECT COUNT(name) FROM users WHERE name = '" + \
                               self.user_name.text() + "'"
                res_name = self.con.execute(checker_name)
                res_name = [it[0] for it in res_name]
                user_registred = True if (int(*res_name)) > 0 else False
                # если такой пользователь существует
                if user_registred:
                    checker_pass = "SELECT password FROM users WHERE name = '" + \
                          self.user_name.text() + "'"
                    res_pass = self.con.execute(checker_pass)
                    res_pass = [it[0] for it in res_pass]
                    if str(*res_pass) != self.user_password.text():
                        raise UserExistsError
                    else:
                        self.registration_label.setText("Ваша учетная запись:")
                        self.setFixedSize(600, 600)
                else:
                    self.registration_label.setText("Ваша учетная запись:")
                    self.setFixedSize(600, 600)
                    res = "INSERT INTO users (name, password) VALUES ('" + \
                          self.user_name.text() + "', '" + \
                          self.user_password.text() + "')"
                    self.cur.execute(res)
                    self.con.commit()

                self.login = self.user_name.text()
                self.password = self.user_password.text()
                self.reg_pass_btn.setText("Выйти из аккаунта")
                self.user_name.setEnabled(False)
                self.user_password.setEnabled(False)
                self.show_hide_pass_btn.show()
                self.change_pass_btn.show()
                self.add_image.show()
                temp_find_image = "SELECT name FROM users WHERE NOT(image IS NULL) AND name = ?"
                temp_find_image = self.cur.execute(temp_find_image, (self.login,)).fetchall()
                temp_find_image = [str(*i) for i in temp_find_image]
                if len(temp_find_image) > 0:
                    self.add_image.setText("Изменить аватар")
                    temp_find_image = "SELECT image FROM users WHERE name = ?"
                    data = self.cur.execute(temp_find_image, (self.login,)).fetchone()
                    with open("tempfile.jpg", "wb") as f:
                        f.write(*data)
                    self.pixmap = QPixmap("tempfile.jpg")
                    self.pixmap = self.pixmap.scaled(130, 130, Qt.KeepAspectRatio)
                    self.image.setPixmap(self.pixmap)
                    self.image.show()
                self.user_password.setText(len(self.password) * "*")
                self.registration = True
                # для карточек
                self.widget_for_modules = QWidget()
                self.box_for_modules = QVBoxLayout()
                self.selected_module = ""
                find_modules = "SELECT modules.name FROM modules, users JOIN " + \
                               "modules_users ON modules.id = modules_users.id_modules " + \
                               "AND users.id = modules_users.id_users WHERE " + \
                               "users.name ='" + self.login + \
                               "'"
                pushbtns = self.cur.execute(find_modules).fetchall()
                self.pushbtns = [QPushButton(str(*i)) for i in pushbtns]

                for i in range(len(self.pushbtns)):
                    self.pushbtns[i].setFixedSize(540, 100)
                    self.box_for_modules.addWidget(self.pushbtns[i])
                    self.pushbtns[i].clicked.connect(self.openmodule)
                
                self.stretchy_spacer_thing = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
                self.box_for_modules.addItem(self.stretchy_spacer_thing)
                self.widget_for_modules.setLayout(self.box_for_modules)
                self.scrollArea.setWidget(self.widget_for_modules)
            else:
                self.registration_label.setText("Пройдите регистрацию:")
                self.add_image.setText("Добавить аватар")
                self.registration = False
                self.setFixedSize(600, 520)
                self.login = ""
                self.password = ""
                self.reg_pass_btn.setText("Подтвердить регистрацию")
                self.user_name.setEnabled(True)
                self.user_password.setEnabled(True)
                self.show_hide_pass_btn.hide()
                self.change_pass_btn.hide()
                self.add_image.hide()
                self.user_name.setText("")
                self.user_password.setText("")
                self.image.hide()
        except UserExistsError:
            self.registration_label.setText("Пользователь с таким именем уже существует\n"
                                            "Если это ваш аккаунт, обратитесь к "
                                            "администратору "
                                            "для выдачи нового пароля, "
                                            "в ином случае выберите другой никнейм.")
        except ZeroNamePassError:
            self.registration_label.setText("Некорректные данные. \nЛогин и пароль "
                                            "обязательны для создания учетной записи!")
        except WrongNameError:
            self.registration_label.setText("В логине возможно использовать только цифры,"
                                            " латинские буквы и символ подчеркивания.\n"
                                            "Длина логина должна быть от 5 до 16 символов")
        except WrongPasswordError:
            self.registration_label.setText("В пароле возможно использовать только цифры,"
                                            " латинские буквы и символ подчеркивания.\n"
                                            "Длина пароля должна быть от 5 до 16 символов")

    def changeMainPage(self, number_of_page):
        self.selected_module = ""
        if self.sender().text() == "Личный кабинет":
            self.stackedWidget.setCurrentIndex(0)
        if self.sender().text() == "Карточки":
            self.stackedWidget.setCurrentIndex(1)
            self.card_stackedWidget.setCurrentIndex(0)
        if self.sender().text() == "Справка":
            self.stackedWidget.setCurrentIndex(2)

    def importing(self):

        temp = "SELECT words.original, words.translation FROM " + \
               "users, words, modules JOIN words_modules, " + \
               "modules_users ON modules.id = words_modules.id_modules " + \
               "AND words.id = words_modules.id_words AND users.id = " + \
               "modules_users.id_users AND modules.id = " + \
               "modules_users.id_modules WHERE users.name = '" + self.login + \
               "' AND modules.name = '" + self.selected_module + "'"
        self.cur.execute(temp)
        file = self.selected_module + ".csv"
        with open(file=file, mode="w", newline='', encoding="utf8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in self.cur.description])
            csv_writer.writerows(self.cur)

    def show_hide_password(self):
        if not self.user_password.isEnabled():
            if self.show_hide_pass_btn.text() == "показать пароль":
                self.user_password.setText(self.password)
                self.show_hide_pass_btn.setText("скрыть пароль")
            else:
                self.user_password.setText(len(self.password) * "*")
                self.show_hide_pass_btn.setText("показать пароль")

    def change_pass(self):
        if not self.user_password.isEnabled():
            self.user_password.setText(self.password)
            self.user_password.setEnabled(True)
        else:
            try:
                if not all(map(lambda i: i in ascii_letters or i.isdigit() or i == "_", self.user_password.text()))\
                        or len(self.user_password.text()) < 5 or len(self.user_password.text()) > 16:
                    raise WrongPasswordError
                update = "UPDATE users SET password = '" + \
                         self.user_password.text() + "' WHERE name = '" + \
                         self.login + "'"
                self.cur.execute(update)
                self.con.commit()
                self.registration_label.setText("Ваша учетная запись:")
                self.password = self.user_password.text()
                self.user_password.setEnabled(False)
                self.user_password.setText(len(self.password) * "*")
            except WrongPasswordError:
                self.registration_label.setText("В пароле возможно использовать только цифры,"
                                                " латинские буквы и символ подчеркивания.\n"
                                                "Длина пароля должна быть от 5 до 16 символов")

    def add_module(self):
        if self.sender().text() == "добавить модуль":
            exists = False
        else:
            exists = True
        self.adding_module = AddNewModule(self, exists)
        self.adding_module.show()

    def openmodule(self):
        self.selected_module = self.sender().text()
        self.card_stackedWidget.setCurrentIndex(1)
        res = "SELECT words.original, words.translation " + \
              "FROM users, words, modules JOIN words_modules," + \
              " modules_users ON modules.id = words_modules.id_modules " + \
              "AND words.id = words_modules.id_words AND users.id = " + \
              "modules_users.id_users AND modules.id = " + \
              "modules_users.id_modules WHERE users.name = '" + self.login + \
              "' AND modules.name = '" + \
              self.sender().text() + "'"
        res = self.cur.execute(res).fetchall()
        self.wordstable.setColumnCount(2)
        self.wordstable.setRowCount(0)
        for i, row in enumerate(res):
            self.wordstable.setRowCount(
                self.wordstable.rowCount() + 1)
            for j, elem in enumerate(row):
                self.wordstable.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        header = self.wordstable.horizontalHeader()
        self.wordstable.setHorizontalHeaderLabels(["Русский язык", "English language"])
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def choose_method(self):
        method, ok_pressed = QInputDialog.getItem(
            self, "Выберите, как хотите изучать слова", "",
            ("Карточки", "Подбор"), 0, False)
        if ok_pressed:
            if method == "Карточки":
                self.learn1()
            elif method == "Подбор":
                self.learn2()

    def learn1(self):
        if self.selected_module != "":
            res = "SELECT words.original, words.translation " + \
                  "FROM users, words, modules JOIN words_modules," + \
                  " modules_users ON modules.id = words_modules.id_modules " + \
                  "AND words.id = words_modules.id_words AND users.id = " + \
                  "modules_users.id_users AND modules.id = " + \
                  "modules_users.id_modules WHERE users.name = '" + self.login + \
                  "' AND modules.name = '" + \
                  self.selected_module + "'"
        else:
            res = "SELECT words.original, words.translation " + \
                  "FROM users, words, modules JOIN words_modules," + \
                  " modules_users ON modules.id = words_modules.id_modules " + \
                  "AND words.id = words_modules.id_words AND users.id = " + \
                  "modules_users.id_users AND modules.id = " + \
                  "modules_users.id_modules WHERE users.name = '" + self.login + \
                  "'"
        res = self.cur.execute(res).fetchall()
        list_of_words = []
        for i, j in enumerate(res):
            list_of_words.append(j)
        self.learning = LearnWordsCards(list_of_words)
        self.learning.show()

    def learn2(self):
        if self.selected_module != "":
            res = "SELECT words.original, words.translation " + \
                  "FROM users, words, modules JOIN words_modules," + \
                  " modules_users ON modules.id = words_modules.id_modules " + \
                  "AND words.id = words_modules.id_words AND users.id = " + \
                  "modules_users.id_users AND modules.id = " + \
                  "modules_users.id_modules WHERE users.name = '" + self.login + \
                  "' AND modules.name = '" + \
                  self.selected_module + "'"
        else:
            res = "SELECT words.original, words.translation " + \
                  "FROM users, words, modules JOIN words_modules," + \
                  " modules_users ON modules.id = words_modules.id_modules " + \
                  "AND words.id = words_modules.id_words AND users.id = " + \
                  "modules_users.id_users AND modules.id = " + \
                  "modules_users.id_modules WHERE users.name = '" + self.login + \
                  "'"
        res = self.cur.execute(res).fetchall()
        list_of_words = []
        for i, j in enumerate(res):
            list_of_words.append(j)
        self.learning = LearnWordChoose(list_of_words)
        self.learning.show()

    def closeEvent(self, event):
        self.con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
