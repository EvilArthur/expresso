import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QInputDialog, QTableWidgetItem, QAction


class Coffee(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        title = ["id", "sort", "roast", "is_ground", "description", "price", "volume"]
        with sqlite3.connect('coffee.db') as self.con:
            self.cur = self.con.cursor()
        self.tableWidget.setColumnCount(len(title))
        self.tableWidget.setHorizontalHeaderLabels(title)
        self.loadTable()
        self.initBar()

    def initBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        add_Coffee = QAction('Add coffee', self)
        add_Coffee.setShortcut("Ctrl+N")
        add_Coffee.triggered.connect(self.addCoffee)
        fileMenu.addAction(add_Coffee)
        editMenu = menubar.addMenu('Edit')
        edit_Coffee = QAction('Edit coffee', self)
        edit_Coffee.setShortcut('Ctrl+E')
        edit_Coffee.triggered.connect(self.editCoffee)
        editMenu.addAction(edit_Coffee)

    def loadTable(self):
        coffee = "SELECT * FROM Coffee"
        data = self.cur.execute(coffee)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(data):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 3:
                    elem = 'молотый' if elem else 'в зёрнах'
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def addCoffee(self):
        res, data = Dialog.getCoffeeData(self)
        if res:
            self.cur.execute("""INSERT INTO Coffee (sort, roast, is_ground, description, price, volume)
            VALUES (%(sort)r, %(roast)r, %(is_ground)d, %(description)r, %(price)d, %(volume)d)""" % data)
            self.con.commit()
            self.loadTable()

    def editCoffee(self):
        id = QInputDialog.getInt(self, 'Введите id', '', 1, 1)[0]
        res, data = Dialog.getCoffeeData(self, edit_data=(1, self.cur, id))
        data['id'] = id
        if res:
            self.cur.execute("""UPDATE Coffee
            SET sort = %(sort)r, 
            roast = %(roast)r, 
            is_ground = %(is_ground)d, 
            description = %(description)r, 
            price = %(price)d, 
            volume = %(volume)d
            WHERE id = %(id)d""" % data)
            self.con.commit()
            self.loadTable()


class Dialog(QDialog):

    def __init__(self, parent, data=None):
        super().__init__(parent)
        uic.loadUi('add.ui', self)
        if data:
            cur, id = data
            old_data = cur.execute("""SELECT * FROM Coffee WHERE id = {}""".format(id)).fetchall()[0]
            self.sort.setText(old_data[1])
            self.roast.setText(old_data[2])
            self.is_ground.setCurrentIndex((old_data[3] - 1) % 2)
            self.description.setPlainText(old_data[4])
            self.price.setValue(old_data[5])
            self.volume.setValue(old_data[6])
        else:
            self.label_id.setVisible(False)
            self.id.setBisible(False)

    def getData(self):
        data = {
            'sort': self.sort.text(), 'roast': self.roast.text(),
            'is_ground': self.is_ground.currentText() == 'Yes', 'description': self.description.toPlainText(),
            'price': self.price.value(), 'volume': self.volume.value()}
        return data

    @staticmethod
    def getCoffeeData(parent, edit_data=(0,)):
        if edit_data[0]:
            dialog = Dialog(parent, edit_data[1:])
        else:
            dialog = Dialog(parent)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getData()
            return (1, data)
        return (0, [])




if __name__ == '__main__':
    app = QApplication(sys.argv)
    coffee = Coffee()
    coffee.show()
    sys.exit(app.exec_())