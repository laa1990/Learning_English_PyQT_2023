from string import ascii_letters

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHeaderView, QSpacerItem, QSizePolicy, QPushButton
from qt.addwordds import Ui_Form


class WrongNameModuleError(Exception):
    pass


class EmptyTableError(Exception):
    pass


class ModuleExistsError(Exception):
    pass


class AddNewModule(QWidget, Ui_Form):
    def __init__(self, main, new_old):
        super().__init__()
        f = open('purple.stylesheet', 'r')
        self.styleData = f.read()
        f.close()
        self.setupUi(self)
        self.setStyleSheet(self.styleData)
        self.exists = new_old
        self.main = main
        self.login = main.login
        self.cur = main.cur
        self.con = main.con
        self.module = main.selected_module
        self.setWindowTitle("Создание нового модуля")
        if self.exists:
            self.lineEdit.setText(main.selected_module)
            self.setWindowTitle("Обновление модуля")
            self.lineEdit.setEnabled(False)
        self.table.setColumnCount(2)  # Set three columns
        self.table.setRowCount(1)
        self.table.setHorizontalHeaderLabels(["Русский язык", "English language"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        # Do the resize of the columns by content
        self.table.resizeColumnsToContents()
        self.add_module_btn.clicked.connect(lambda checked, main=main: self.add_module(main))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)
        if event.key() == Qt.Key_Delete and event.modifiers() == Qt.ControlModifier:
            self.table.removeRow(self.table.rowCount() - 1)

    def add_module(self, main):
        try:
            if not self.exists:
                if self.lineEdit.text() == "" or not all(map(
                        lambda i: i in ascii_letters or i.isdigit() or i == "_" or i.lower() in
                        "ёйцукенгшщзхъфывапролджэячсмитьбю",
                        self.lineEdit.text())) or len(self.lineEdit.text()) < 3 or len(self.lineEdit.text()) > 16:
                    raise WrongNameModuleError
                if self.table.rowCount() == 0:
                    raise EmptyTableError
                for col in range(2):
                    for row in range(self.table.rowCount()):
                        if self.table.item(row, col) is None:
                            raise EmptyTableError
                check_module = """SELECT modules.name 
                FROM modules, users JOIN modules_users 
                ON users.id = modules_users.id_users AND 
                modules.id = modules_users.id_modules 
                WHERE users.name = '""" + self.login + "'"
                res = self.cur.execute(check_module).fetchall()
                res = [str(*i) for i in res]
                if self.lineEdit.text() in res:
                    raise ModuleExistsError
                add_module = "INSERT INTO modules (name) VALUES ('" + self.lineEdit.text() + "');"
                self.cur.execute(add_module)
                self.con.commit()
                add_module = "INSERT INTO modules_users (id_modules,id_users) VALUES " \
                             "((SELECT id FROM modules ORDER BY id DESC LIMIT 1),(SELECT id " \
                             "FROM users WHERE name = '" + self.login + "'));"
                self.cur.execute(add_module)
                self.con.commit()
                for i in range(self.table.rowCount()):
                    add_word = "INSERT INTO words (original, translation) " \
                               "VALUES ('" + self.table.item(i, 0).text() + "', '" + \
                               self.table.item(i, 1).text() + "');"
                    self.cur.execute(add_word)
                    self.con.commit()
                    add_word = "INSERT INTO words_modules (id_modules, id_words)" + \
                               "VALUES ((SELECT id FROM modules ORDER BY id DESC LIMIT 1), " \
                               "(SELECT id FROM words ORDER BY id DESC LIMIT 1));"
                    self.cur.execute(add_word)
                    self.con.commit()
                    # добавление кнопки в box_for_modules
                    temp = QPushButton(self.lineEdit.text())
                    temp.setFixedSize(540, 100)
                    main.box_for_modules.addWidget(temp)
                    temp.clicked.connect(main.openmodule)
                    self.stretchy_spacer_thing = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
                    main.box_for_modules.addItem(self.stretchy_spacer_thing)
            else:
                if self.table.rowCount() == 0:
                    raise EmptyTableError
                for col in range(2):
                    for row in range(self.table.rowCount()):
                        if self.table.item(row, col) is None:
                            raise EmptyTableError
                for i in range(self.table.rowCount()):
                    add_word = "INSERT INTO words (original, translation) " \
                               "VALUES ('" + self.table.item(i, 0).text() + "', '" + \
                               self.table.item(i, 1).text() + "');"
                    self.cur.execute(add_word)
                    self.con.commit()
                    add_word = "INSERT INTO words_modules (id_modules, id_words)" + \
                               "VALUES ((SELECT modules.id FROM modules, users JOIN " + \
                               "modules_users ON modules.id = modules_users.id_modules " + \
                               "AND users.id = modules_users.id_users WHERE users.name = '" + \
                               self.login + "' AND modules.name = '" + self.module + "'), " + \
                               "(SELECT id FROM words ORDER BY id DESC LIMIT 1));"
                    self.cur.execute(add_word)
                    self.con.commit()

            self.close()
        except WrongNameModuleError:
            self.error.setText("Название модуля должно содержать от 3"
                               "до 16 символов русского или латинского "
                               "алфавита, '_' и цифры")
        except EmptyTableError:
            self.error.setText("Таблица не содержит ни "
                               "одной строки или некоторые ячейки пусты."
                               " заполните их или удалите пустующие строки в "
                               "конце таблицы")
        except ModuleExistsError:
            self.error.setText("У Вас уже есть модуль с таким именем. "
                               "Придумайте другое имя для своего же "
                               "удобства.")

