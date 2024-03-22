from PyQt5.QtWidgets import QApplication, QMainWindow, QCalendarWidget, QWidget, QVBoxLayout, QPushButton, QMessageBox, \
    QStackedLayout, QLabel, QGroupBox, QMenu, QAction, QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, \
    QComboBox, QCompleter
from PyQt5.QtCore import QDate, QLocale
import sys
from database_connection import mydb
import pandas as pd


class DatabaseWidget(QWidget):
    def __init__(self, main_app, parent):
        super().__init__(parent)
        self.main_app = main_app

        self.layout = QVBoxLayout()

        self.table = QTableWidget()

        # Disallow editing of the table
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.layout.addWidget(self.table)

        # Opcja służy dodawaniu nowych odbiorców
        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.parent().show_add_recipient_widget)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

        # Fetch data from the database and populate the table
        self.refresh()

        # Connect the itemClicked signal to the handler function
        self.table.itemClicked.connect(self.handle_click)

    def refresh(self):
        """
        This function refreshes the data in the table by querying the database again
        """
        mycursor = mydb.cursor()

        # Execute a query to the database
        mycursor.execute("SELECT ID, NazwaSklepu, SkroconaNazwa, Miasto, Ulica, NumerBudynku, KodPocztowy, NIP, StalyRabat FROM Odbiorcy")

        # Fetch all rows from the result of the query
        myresult = mycursor.fetchall()

        # Clear the table
        self.table.setRowCount(0)

        # Set the number of columns
        self.table.setColumnCount(9)
        # Set the column names
        self.table.setHorizontalHeaderLabels(["ID", "NazwaSklepu", "SkroconaNazwa", "Miasto", "Ulica", "NumerBudynku", "KodPocztowy", "NIP", "StalyRabat"])

        # Add rows to the table
        for row_number, row_data in enumerate(myresult):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        self.table.hideColumn(0)  # Hide the ID column

    def handle_click(self, item):
        index = item.row()
        selected_data = [self.table.item(index, i).text() for i in range(self.table.columnCount())]
        selected_shop = self.table.item(index, 1).text()  # Changed from 0 to 1

        print(f"Selected data: {selected_data}")
        # Show a confirmation dialog
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(f"Czy chcesz zmodyfikować {selected_shop}?")
        msg_box.setWindowTitle("Potwierdzenie")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        retval = msg_box.exec_()
        if retval == QMessageBox.Ok:
            self.main_app.show_update_recipient_widget(selected_data)


class ProductsDatabaseWidget(QWidget):
    def __init__(self, main_app, parent):
        super().__init__(parent)
        self.main_app = main_app

        self.layout = QVBoxLayout()

        self.table = QTableWidget()

        # Disallow editing of the table
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.layout.addWidget(self.table)

        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.parent().show_add_product_widget)  # załóżmy, że masz taką funkcję w głównej klasie aplikacji
        self.layout.addWidget(self.add_button)


        self.setLayout(self.layout)

        # Fetch data from the database and populate the table
        self.refresh()

    def refresh(self):
        """
        This function refreshes the data in the table by querying the database again
        """
        mycursor = mydb.cursor()

        # Execute a query to the database
        mycursor.execute("SELECT ID, NazwaProduktu, Cena FROM Produkty")

        # Fetch all rows from the result of the query
        myresult = mycursor.fetchall()

        # Clear the table
        self.table.setRowCount(0)

        # Set the number of columns
        self.table.setColumnCount(3)
        # Set the column names
        self.table.setHorizontalHeaderLabels(["ID", "NazwaProduktu", "Cena"])

        # Add rows to the table
        for row_number, row_data in enumerate(myresult):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        self.table.hideColumn(0)  # Hide the ID column


class AddProductWidget(QWidget):
    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app

        layout = QVBoxLayout()

        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Nazwa Produktu")
        layout.addWidget(self.product_name_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Cena")
        layout.addWidget(self.price_input)

        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_product)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def reset_form(self):
        """
        This function clears all the QLineEdit fields in the form.
        """
        self.product_name_input.clear()
        self.price_input.clear()

    def add_product(self):
        """
        Funckja służy dodaniu zedytowanych elementów do bazy danych
        """
        product_name = self.product_name_input.text()
        price = self.price_input.text()

        # Create the message box
        msg = QMessageBox()
        msg.setWindowTitle("Potwierdzenie danych")
        msg.setText(f"Zostaną dodane następujące dane:\n"
                    f"Nazwa Produktu: {product_name}\n"
                    f"Cena: {price}\n"
                    f"Czy są poprawne?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Tak")
        msg.button(QMessageBox.No).setText("Nie")
        result = msg.exec_()

        if result == QMessageBox.Yes:
            mycursor = mydb.cursor()
            try:
                sql = "INSERT INTO Produkty (NazwaProduktu, Cena) VALUES (%s, %s)"
                val = (product_name, price)
                mycursor.execute(sql, val)

                mydb.commit()

                QMessageBox.information(self, "Sukces", "Dodano nowy produkt")

                # Clear the form
                self.reset_form()

                # Refresh the database view
                self.main_app.products_database_widget.refresh()

                # Switch back to the database widget
                self.main_app.show_products_database_widget()

                # Go back to the previous view
                self.main_app.go_back()
                self.main_app.go_back()

            finally:
                mycursor.close()


class AllDatabaseWidget(QWidget):
    def showEvent(self, event):
        self.refresh()
        super(AllDatabaseWidget, self).showEvent(event)

    def __init__(self, main_app, parent):
        super().__init__(parent)
        self.main_app = main_app

        self.layout = QVBoxLayout()

        self.table = QTableWidget()

        # Disallow editing of the table
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        # Fetch data from the database and populate the table
        self.refresh()

    def refresh(self):
        """
        This function refreshes the data in the table by querying the database again
        """
        mydb.reconnect()
        mycursor = mydb.cursor()

        # Execute a query to the database with an additional column for 'Suma'
        query = """
        SELECT ID, Data, NazwaSklepu, Przychod, Zwrot, (Przychod - Zwrot) as Suma
        FROM PodsumowanieKosztow
        """
        mycursor.execute(query)

        # Fetch all rows from the result of the query
        myresult = mycursor.fetchall()

        # Clear the table
        self.table.setRowCount(0)

        # Set the number of columns
        self.table.setColumnCount(6)  # Added one more column for 'Suma'
        # Set the column names
        self.table.setHorizontalHeaderLabels(["ID", "Data", "NazwaSklepu", "Przychod", "Zwrot", "Suma"])

        # Add rows to the table
        for row_number, row_data in enumerate(myresult):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        self.table.hideColumn(0)  # Hide the ID column


class DailyDatabaseWidget(QWidget):
    def showEvent(self, event):
        self.refresh()
        super(DailyDatabaseWidget, self).showEvent(event)

    def __init__(self, main_app, parent):
        super().__init__(parent)
        self.main_app = main_app

        self.layout = QVBoxLayout()

        self.table = QTableWidget()

        # Disallow editing of the table
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        # Fetch data from the database and populate the table
        self.refresh()

    def refresh(self):
        """
        This function refreshes the data in the table by querying the database again
        """
        mycursor = mydb.cursor()

        # Get the selected date and convert it to string format
        selected_date = self.main_app.get_selected_date().toString("yyyy-MM-dd")

        # Execute a query to the database with an additional column for 'Suma'
        # and filtering results based on the selected date
        query = """
        SELECT ID, Data, NazwaSklepu, Przychod, Zwrot, (Przychod - Zwrot) as Suma
        FROM PodsumowanieKosztow
        WHERE Data = %s
        """
        mycursor.execute(query, (selected_date,))

        # Fetch all rows from the result of the query
        myresult = mycursor.fetchall()

        # Clear the table
        self.table.setRowCount(0)

        # Set the number of columns
        self.table.setColumnCount(6)  # Added one more column for 'Suma'
        # Set the column names
        self.table.setHorizontalHeaderLabels(["ID", "Data", "NazwaSklepu", "Przychod", "Zwrot", "Suma"])

        # Add rows to the table
        for row_number, row_data in enumerate(myresult):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        self.table.hideColumn(0)  # Hide the ID column


class MainMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        # Stwórz menu dla button1
        self.menu1 = QMenu()
        self.menu2 = QMenu()
        self.menu3 = QMenu()
        self.menu4 = QMenu()
        self.menu5 = QMenu()

        # menu1
        action1 = QAction("Sprzedaż" + " " * 50, self)
        action1.triggered.connect(self.parent().show_shop_name_database)  # Połącz akcję z metodą
        self.menu1.addAction(action1)

        action2 = QAction("Pezety" + " " * 50, self)  # dodanie spacji zeby bylo szersze
        action2.triggered.connect(self.parent().show_new_widget)  # Połącz akcję z inną metodą
        self.menu1.addAction(action2)

        # menu2
        action3 = QAction("Odbiorcy" + " " * 50, self)
        action3.triggered.connect(self.parent().show_database_widget)  # Connect action with showing new widget
        self.menu2.addAction(action3)

        action4 = QAction("Towary" + " " * 50, self)
        action4.triggered.connect(self.parent().show_products_database_widget)
        self.menu2.addAction(action4)

        action5 = QAction("Przychód roczny" + " " * 50, self)
        mydb.reconnect()
        action5.triggered.connect(self.parent().show_all_database_widget)
        self.menu2.addAction(action5)

        action6 = QAction("Przychód dienny" + " " * 50, self)
        mydb.reconnect()
        action6.triggered.connect(self.parent().show_daily_database_widget)
        self.menu2.addAction(action6)

        # menu3
        action7 = QAction("Wydruki" + " " * 50, self)
        # action6.triggered.connect(self.parent().show_new_widget)
        self.menu3.addAction(action6)

        # menu4
        action8 = QAction("Statystyki" + " " * 50, self)
        # action7.triggered.connect(self.parent().show_new_widget)
        self.menu4.addAction(action7)

        # menu5
        action9 = QAction("Zmiana nagłówka" + " " * 50, self)
        # action8.triggered.connect(self.parent().show_new_widget)
        self.menu5.addAction(action8)

        button1 = QPushButton('Sprzedaż')
        button1.setMenu(self.menu1)  # Ustaw menu dla button1
        button1.setStyleSheet(
            "QPushButton { font-size: 20px; width: 200px; height: 50px; }")  # Zwiększ rozmiar czcionki

        button2 = QPushButton('Bazy')
        button2.setMenu(self.menu2)
        button2.setStyleSheet(
            "QPushButton { font-size: 20px; width: 200px; height: 50px; }")  # Zwiększ rozmiar czcionki

        button3 = QPushButton('Wydruki')
        button3.setMenu(self.menu3)
        button3.setStyleSheet(
            "QPushButton { font-size: 20px; width: 200px; height: 50px; }")  # Zwiększ rozmiar czcionki

        button4 = QPushButton('Statystyki')
        button4.setMenu(self.menu4)
        button4.setStyleSheet(
            "QPushButton { font-size: 20px; width: 200px; height: 50px; }")  # Zwiększ rozmiar czcionki

        button5 = QPushButton('Inne')
        button5.setMenu(self.menu5)
        button5.setStyleSheet(
            "QPushButton { font-size: 20px; width: 200px; height: 50px; }")  # Zwiększ rozmiar czcionki

        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)
        layout.addWidget(button4)
        layout.addWidget(button5)

        self.setLayout(layout)

        # Zwiększ rozmiar czcionki w rozwijanym menu
        self.menu1.setStyleSheet("QMenu { font-size: 20px; } QMenu::item { height: 50px; }")
        self.menu2.setStyleSheet("QMenu { font-size: 20px; } QMenu::item { height: 50px; }")
        self.menu3.setStyleSheet("QMenu { font-size: 20px; } QMenu::item { height: 50px; }")
        self.menu4.setStyleSheet("QMenu { font-size: 20px; } QMenu::item { height: 50px; }")
        self.menu5.setStyleSheet("QMenu { font-size: 20px; } QMenu::item { height: 50px; }")


class NewWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel("To jest nowy widżet!")

        layout.addWidget(label)

        self.setLayout(layout)


class Income(QWidget):
    def __init__(self, main_app, shop_name=None, date=None):
        super().__init__()

        self.main_app = main_app  # store the reference to main_app

        layout = QVBoxLayout()

        self.label = QLabel()
        layout.addWidget(self.label)  # add widget to layout (widok uzytkownika)

        # Add a second calendar for choosing the date to copy from
        self.copy_from_calendar = QCalendarWidget()
        self.copy_from_calendar.setGridVisible(True)
        polish_locale = QLocale(QLocale.Polish, QLocale.Poland)
        self.copy_from_calendar.setLocale(polish_locale)
        layout.addWidget(self.copy_from_calendar)

        # Add a "Copy" button
        self.copy_button = QPushButton("Kopiuj")
        self.copy_button.clicked.connect(self.copy_row)
        layout.addWidget(self.copy_button)

        # Add a table to display the row to be copied
        self.preview_table = QTableWidget()
        layout.addWidget(self.preview_table)

        # Add a "Dodaj do bazy danych" button
        self.add_to_db_button = QPushButton("Dodaj do bazy danych")
        self.add_to_db_button.clicked.connect(self.insert_row_into_database)
        self.add_to_db_button.setEnabled(False)  # Disable the button initially
        layout.addWidget(self.add_to_db_button)

        self.edit_button = QPushButton("Edytuj")
        self.edit_button.clicked.connect(self.toggle_table_editability)
        layout.addWidget(self.edit_button)

        self.save_again_button = QPushButton("Zapisz zmiany w bazie")
        self.save_again_button.clicked.connect(self.save_changes_to_database)
        layout.addWidget(self.save_again_button)

        self.setLayout(layout)

        # self.update_shop_name_and_date(shop_name, date)

    def update_shop_name_and_date(self, shop_name, date):
        self.shop_name = shop_name
        self.date = date
        self.label.setText(f"Widzet przychody! Nazwa sklepu: {self.shop_name}, Data: {self.date}")

        # Create a cursor
        mycursor = mydb.cursor()

        # Execute a query to the database
        mycursor.execute(f"SELECT * FROM {self.shop_name}_p WHERE Data = '{date}'")

        # Fetch all rows from the result of the query
        myresult = mycursor.fetchall()

        # Remove the old table widget from the layout (if it exists)
        if hasattr(self, 'table_widget'):
            self.layout().removeWidget(self.table_widget)
            self.table_widget.deleteLater()
            self.table_widget = None

        if myresult:
            # Create a DataFrame from the result
            df = pd.DataFrame(myresult, columns=[i[0] for i in mycursor.description])

            # Create two new DataFrames: one for the "Produkt" column and one for the "Ilosc" column
            df_produkt = df[[f'Produkt{i}' for i in range(1, 16)]].melt(var_name='Produkt')
            df_ilosc = df[[f'Ilosc{i}' for i in range(1, 16)]].melt(var_name='Ilosc')

            # Combine the two DataFrames into one
            df_long = pd.concat([df_produkt['value'], df_ilosc['value']], axis=1)
            df_long.columns = ['Produkt', 'Ilosc']

            # Replace None with "Puste"
            df_long.fillna("-----", inplace=True)

            # Drop any rows with missing values (usuwa te None i sie nie wyswietlaja)
            # df_long = df_long.dropna()
        else:
            # Create a DataFrame with two rows of "Brak"
            df_long = pd.DataFrame({'Produkt': ['Brak', 'Brak'], 'Ilosc': ['Brak', 'Brak']})
            QMessageBox.information(self, "Brak danych", "Brak danych na wybraną datę")

        # Create a new table widget
        self.table_widget = TableWidget(df_long, self)

        # Add the new table widget to the layout
        self.layout().addWidget(self.table_widget)

    def copy_row(self):
        kopiuj_z_daty = self.copy_from_calendar.selectedDate().toPyDate()

        # Stworzenie kursora
        mycursor = mydb.cursor()

        # Wykonanie zapytania do bazy danych, aby pobrać wiersz do skopiowania
        mycursor.execute(f"SELECT * FROM {self.shop_name}_p WHERE Data = '{kopiuj_z_daty}'")
        self.wiersz_do_skopiowania = mycursor.fetchone()

        if self.wiersz_do_skopiowania is not None:
            # Display the row in the preview_table
            self.display_row_in_table(self.wiersz_do_skopiowania)
            self.add_to_db_button.setEnabled(True)  # Enable the "Dodaj do bazy danych" button

        else:
            QMessageBox.information(self, "Brak danych", "Brak danych na wybraną datę, nie można skopiować wiersza")

    def display_row_in_table(self, row):
        # Zdefiniuj liczbę par kolumn produktów i ilości
        liczba_par_kolumn_do_skopiowania = 15

        # Przygotuj listy dla produktów i ilości
        produkty = [row[i] for i in range(2, liczba_par_kolumn_do_skopiowania * 2 + 1, 2)]
        ilosci = [row[i] for i in range(3, liczba_par_kolumn_do_skopiowania * 2 + 2, 2)]

        # Ustaw liczbę wierszy i kolumn tabeli
        self.preview_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # zeby nie mozna bylo edytowac
        self.preview_table.setRowCount(liczba_par_kolumn_do_skopiowania)
        self.preview_table.setColumnCount(2)
        self.preview_table.setHorizontalHeaderLabels(["Produkt", "Ilość"])

        # Wypełnij tabelę danymi
        for idx, (produkt, ilosc) in enumerate(zip(produkty, ilosci)):
            # Zamień None na "Puste" - ale dalej jest jako None?
            produkt_display = "-----" if produkt is None else str(produkt)
            ilosc_display = "-----" if ilosc is None else str(ilosc)

            self.preview_table.setItem(idx, 0, QTableWidgetItem(produkt_display))
            self.preview_table.setItem(idx, 1, QTableWidgetItem(ilosc_display))

    def insert_row_into_database(self):
        kopiuj_na_date = self.main_app.get_selected_date().toPyDate()

        # Zdefiniuj liczbę par kolumn produktów i ilości, które chcesz skopiować (bez kolumny daty)
        liczba_par_kolumn_do_skopiowania = 15

        # Przygotowanie wartości
        produkty_ilosci = [self.wiersz_do_skopiowania[i] for i in range(2, liczba_par_kolumn_do_skopiowania * 2 + 2)]
        wartosci = [kopiuj_na_date] + produkty_ilosci

        # Przygotowanie polecenia SQL
        kolumny = ', '.join([f'Produkt{i}, Ilosc{i}' for i in range(1, liczba_par_kolumn_do_skopiowania + 1)])
        placeholders = ', '.join(['%s'] * (liczba_par_kolumn_do_skopiowania * 2))
        sql = f"INSERT INTO {self.shop_name}_p (Data, {kolumny}) VALUES (%s, {placeholders})"

        # Utworzenie kursora
        mycursor = mydb.cursor()
        mycursor.execute(sql, wartosci)
        mydb.commit()

        QMessageBox.information(self, "Sukces", "Skopiowano wiersz")

        # Refresh the table
        self.update_shop_name_and_date(self.shop_name, kopiuj_na_date)

        # Clear the preview table and disable the "Dodaj do bazy danych" button
        self.preview_table.clear()
        self.add_to_db_button.setEnabled(False)

    def toggle_table_editability(self):
        current_values = []

        # Jeśli tabela nie jest edytowalna, uczyn ją edytowalną
        if self.table_widget.table.editTriggers() == QTableWidget.NoEditTriggers:
            self.table_widget.table.setEditTriggers(QTableWidget.AllEditTriggers)
            QMessageBox.information(self, "Edycja", "Rozpoczęto edycję")
            self.edit_button.setText("Zakończ edycję")

            # Przechowuj aktualne wartości dla każdego wiersza w kolumnie "Produkt"
            for row in range(self.table_widget.table.rowCount()):
                current_item = self.table_widget.table.item(row, 0)
                current_values.append(current_item.text() if current_item else "")

                # Ustaw rozwijaną listę dla produktu dla każdego wiersza
                self.set_dropdown_for_product(row, current_values[row])

        # Jeśli tabela jest edytowalna, uczyn ją nieedytowalną
        else:
            self.table_widget.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.edit_button.setText("Edytuj")
            for row in range(self.table_widget.table.rowCount()):
                combo = self.table_widget.table.cellWidget(row, 0)
                if combo:
                    # Zapisz wartość wybraną z QComboBox jako element tabeli
                    current_text = combo.currentText()
                    self.table_widget.table.setItem(row, 0, QTableWidgetItem(current_text))
                    # Usuń QComboBox
                    self.table_widget.table.removeCellWidget(row, 0)

    def set_dropdown_for_product(self, row, current_value):
        combobox = QComboBox()
        product_list = self.get_product_list_from_db()
        combobox.addItems(product_list)

        # Uczyń QComboBox edytowalnym
        combobox.setEditable(True)

        # Dodaj QCompleter dla QComboBox
        completer = QCompleter(product_list)
        combobox.setCompleter(completer)

        # Ustaw bieżącą wartość na wcześniej wybraną
        combobox.setCurrentText(current_value)

        combobox.currentIndexChanged.connect(lambda: self.update_table_item(row, combobox))
        self.table_widget.table.setCellWidget(row, 0, combobox)

    def get_product_list_from_db(self):
        mycursor = mydb.cursor()
        mycursor.execute("SELECT NazwaProduktu FROM Produkty")
        result = mycursor.fetchall()
        return [item[0] for item in result]

    def save_changes_to_database(self):
        # Przygotuj kolumny do aktualizacji
        produkt_columns = [f"Produkt{i}" for i in range(1, 16)]  # lista produkt1 itd (numeracja w tej tabeli chyba)
        ilosc_columns = [f"Ilosc{i}" for i in range(1, 16)]

        # Odczytaj dane z tabeli i przygotuj dane do aktualizacji
        update_data = []
        for row in range(self.table_widget.table.rowCount()):
            produkt_item = self.table_widget.table.cellWidget(row, 0)  # produkty w kolumnie 0 (cellWidget)
            ilosc_item = self.table_widget.table.item(row, 1)  # ilosci w kolumnie 1
            # Odczytaj wartość z QComboBox
            prod = produkt_item.currentText() if produkt_item and produkt_item.currentText() != "" else None
            il = ilosc_item.text() if ilosc_item and ilosc_item.text() != "" else None
            il = None if il == "-----" else il
            #print(f"Produkt z QComboBox: {produkt_item.currentText() if produkt_item else 'Brak produkt_item'}")
            #print(f"Ilość z QTableWidgetItem: {ilosc_item.text() if ilosc_item else 'Brak ilosc_item'}")
            #print(f"Przypisane wartości - prod: {prod}, il: {il}")

            if prod is None or self.product_exists_in_db(prod):
                update_data.append((prod, il, produkt_columns[row], ilosc_columns[row]))

        # Aktualizuj bazę danych
        mycursor = mydb.cursor()
        for prod, il, prod_col, ilosc_col in update_data:
            try:
                sql = f"UPDATE {self.shop_name}_p SET {prod_col} = %s, {ilosc_col} = %s WHERE Data = %s"
                mycursor.execute(sql, (prod, il, self.date))
                mydb.commit()
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas aktualizacji bazy danych: {e}")
                return  # Return early if there's an error

        QMessageBox.information(self, "Sukces", "Zaktualizowano dane w bazie danych")

        #dodawanie do PodsumowanieKosztow
        laczny_przychod = 0

        for prod, il, prod_col, ilosc_col in update_data:
            mycursor = mydb.cursor()
            sql = f"SELECT Cena FROM Produkty WHERE NazwaProduktu = %s"
            mycursor.execute(sql, (prod,)) #cause we have to have at least tuple
            result = mycursor.fetchall()
            price = result[0][0]  # Assuming price is the first field in the first row

            il = float(il)
            price = float(price)

            przychod = price * il
            laczny_przychod += przychod

        laczny_przychod = round(laczny_przychod, 2)

        #print('to jest laczny przychod: ', laczny_przychod)

        mycursor = mydb.cursor()
        sql = f"SELECT Przychod FROM PodsumowanieKosztow WHERE Data = %s and NazwaSklepu = %s"
        mycursor.execute(sql, (self.date, self.shop_name))
        wiersz_istnieje = mycursor.fetchall()

        if wiersz_istnieje:
            mycursor = mydb.cursor()
            sql = "UPDATE PodsumowanieKosztow SET Przychod = %s WHERE Data = %s and NazwaSklepu = %s"
            mycursor.execute(sql, (laczny_przychod, self.date, self.shop_name))
            mydb.commit()
            #print("istnieje")
        else:
            mycursor = mydb.cursor()
            sql = "INSERT INTO PodsumowanieKosztow (Data, NazwaSklepu, Przychod) VALUES (%s, %s, %s)"
            val = (self.date, self.shop_name, laczny_przychod)
            mycursor.execute(sql, val)
            mydb.commit()
            #print("stworze nowy wiersz")

    #def save_to_przychod_podsumowaniekosztow(self):
    def update_table_item(self, row, combobox):  # Nowa metoda
        self.table_widget.table.setItem(row, 0, QTableWidgetItem(combobox.currentText()))

    def product_exists_in_db(self, product_name):
        '''sprawdzamy czy produkt w ogole sie znajduje w tej tabeli produkty bo kod sam jakos nie wiem czemu
        nam nie aktualizuje tej tabeli jak jest None, nie wiem może nie przyjmuje NULL jako sama ta baza danych
        i jest problem zeby jako produkt dac wartosc null, nie da sie jak jest ten klucz obcy'''
        mycursor = mydb.cursor()
        query = "SELECT COUNT(*) FROM produkty WHERE NazwaProduktu = %s"
        mycursor.execute(query, (product_name,))
        result = mycursor.fetchone()
        return result[0] > 0


# Do the same for Return


class Return(QWidget):
    def __init__(self, main_app, shop_name=None, date=None):
        super().__init__()

        self.main_app = main_app  # store the reference to main_app

        layout = QVBoxLayout()

        self.label = QLabel()
        layout.addWidget(self.label)  # add widget to layout (widok uzytkownika)

        # Add a second calendar for choosing the date to copy from
        self.copy_from_calendar = QCalendarWidget()
        self.copy_from_calendar.setGridVisible(True)
        polish_locale = QLocale(QLocale.Polish, QLocale.Poland)
        self.copy_from_calendar.setLocale(polish_locale)
        layout.addWidget(self.copy_from_calendar)

        # Add a "Copy" button
        self.copy_button = QPushButton("Kopiuj")
        self.copy_button.clicked.connect(self.copy_row)
        layout.addWidget(self.copy_button)

        # Add a table to display the row to be copied
        self.preview_table = QTableWidget()
        layout.addWidget(self.preview_table)

        # Add a "Dodaj do bazy danych" button
        self.add_to_db_button = QPushButton("Dodaj do bazy danych")
        self.add_to_db_button.clicked.connect(self.insert_row_into_database)
        self.add_to_db_button.setEnabled(False)  # Disable the button initially
        layout.addWidget(self.add_to_db_button)

        self.edit_button = QPushButton("Edytuj")
        self.edit_button.clicked.connect(self.toggle_table_editability)
        layout.addWidget(self.edit_button)

        self.save_again_button = QPushButton("Zapisz zmiany w bazie")
        self.save_again_button.clicked.connect(self.save_changes_to_database)
        layout.addWidget(self.save_again_button)

        self.setLayout(layout)

        # self.update_shop_name_and_date(shop_name, date)

    def update_shop_name_and_date(self, shop_name, date):
        self.shop_name = shop_name
        self.date = date
        self.label.setText(f"Widzet zwroty! Nazwa sklepu: {self.shop_name}, Data: {self.date}")

        # Create a cursor
        mycursor = mydb.cursor()

        # Execute a query to the database
        mycursor.execute(f"SELECT * FROM {self.shop_name}_z WHERE Data = '{date}'")

        # Fetch all rows from the result of the query
        myresult = mycursor.fetchall()

        # Remove the old table widget from the layout (if it exists)
        if hasattr(self, 'table_widget'):
            self.layout().removeWidget(self.table_widget)
            self.table_widget.deleteLater()
            self.table_widget = None

        if myresult:
            # Create a DataFrame from the result
            df = pd.DataFrame(myresult, columns=[i[0] for i in mycursor.description])

            # Create two new DataFrames: one for the "Produkt" column and one for the "Ilosc" column
            df_produkt = df[[f'Produkt{i}' for i in range(1, 16)]].melt(var_name='Produkt')
            df_ilosc = df[[f'Ilosc{i}' for i in range(1, 16)]].melt(var_name='Ilosc')

            # Combine the two DataFrames into one
            df_long = pd.concat([df_produkt['value'], df_ilosc['value']], axis=1)
            df_long.columns = ['Produkt', 'Ilosc']

            # Replace None with "Puste"
            df_long.fillna("-----", inplace=True)

            # Drop any rows with missing values (usuwa te None i sie nie wyswietlaja)
            # df_long = df_long.dropna()
        else:
            # Create a DataFrame with two rows of "Brak"
            df_long = pd.DataFrame({'Produkt': ['Brak', 'Brak'], 'Ilosc': ['Brak', 'Brak']})
            QMessageBox.information(self, "Brak danych", "Brak danych na wybraną datę")

        # Create a new table widget
        self.table_widget = TableWidget(df_long, self)

        # Add the new table widget to the layout
        self.layout().addWidget(self.table_widget)

    def copy_row(self):
        kopiuj_z_daty = self.copy_from_calendar.selectedDate().toPyDate()

        # Stworzenie kursora
        mycursor = mydb.cursor()

        # Wykonanie zapytania do bazy danych, aby pobrać wiersz do skopiowania
        mycursor.execute(f"SELECT * FROM {self.shop_name}_z WHERE Data = '{kopiuj_z_daty}'")
        self.wiersz_do_skopiowania = mycursor.fetchone()

        if self.wiersz_do_skopiowania is not None:
            # Display the row in the preview_table
            self.display_row_in_table(self.wiersz_do_skopiowania)
            self.add_to_db_button.setEnabled(True)  # Enable the "Dodaj do bazy danych" button

        else:
            QMessageBox.information(self, "Brak danych", "Brak danych na wybraną datę, nie można skopiować wiersza")

    def display_row_in_table(self, row):
        # Zdefiniuj liczbę par kolumn produktów i ilości
        liczba_par_kolumn_do_skopiowania = 15

        # Przygotuj listy dla produktów i ilości
        produkty = [row[i] for i in range(2, liczba_par_kolumn_do_skopiowania * 2 + 1, 2)]
        ilosci = [row[i] for i in range(3, liczba_par_kolumn_do_skopiowania * 2 + 2, 2)]

        # Ustaw liczbę wierszy i kolumn tabeli
        self.preview_table.setEditTriggers(QAbstractItemView.NoEditTriggers) #zeby nie mozna bylo edytowac
        self.preview_table.setRowCount(liczba_par_kolumn_do_skopiowania)
        self.preview_table.setColumnCount(2)
        self.preview_table.setHorizontalHeaderLabels(["Produkt", "Ilość"])

        # Wypełnij tabelę danymi
        for idx, (produkt, ilosc) in enumerate(zip(produkty, ilosci)):
            # Zamień None na "Puste" - ale dalej jest jako None?
            produkt_display = "-----" if produkt is None else str(produkt)
            ilosc_display = "-----" if ilosc is None else str(ilosc)

            self.preview_table.setItem(idx, 0, QTableWidgetItem(produkt_display))
            self.preview_table.setItem(idx, 1, QTableWidgetItem(ilosc_display))

    def insert_row_into_database(self):
        kopiuj_na_date = self.main_app.get_selected_date().toPyDate()

        # Zdefiniuj liczbę par kolumn produktów i ilości, które chcesz skopiować (bez kolumny daty)
        liczba_par_kolumn_do_skopiowania = 15

        # Przygotowanie wartości
        produkty_ilosci = [self.wiersz_do_skopiowania[i] for i in range(2, liczba_par_kolumn_do_skopiowania * 2 + 2)]
        wartosci = [kopiuj_na_date] + produkty_ilosci

        # Przygotowanie polecenia SQL
        kolumny = ', '.join([f'Produkt{i}, Ilosc{i}' for i in range(1, liczba_par_kolumn_do_skopiowania + 1)])
        placeholders = ', '.join(['%s'] * (liczba_par_kolumn_do_skopiowania * 2))
        sql = f"INSERT INTO {self.shop_name}_z (Data, {kolumny}) VALUES (%s, {placeholders})"

        # Utworzenie kursora
        mycursor = mydb.cursor()
        mycursor.execute(sql, wartosci)
        mydb.commit()

        QMessageBox.information(self, "Sukces", "Skopiowano wiersz")

        # Refresh the table
        self.update_shop_name_and_date(self.shop_name, kopiuj_na_date)

        # Clear the preview table and disable the "Dodaj do bazy danych" button
        self.preview_table.clear()
        self.add_to_db_button.setEnabled(False)

    def toggle_table_editability(self):
        current_values = []

        # Jeśli tabela nie jest edytowalna, uczyn ją edytowalną
        if self.table_widget.table.editTriggers() == QTableWidget.NoEditTriggers:
            self.table_widget.table.setEditTriggers(QTableWidget.AllEditTriggers)
            QMessageBox.information(self, "Edycja", "Rozpoczęto edycję")
            self.edit_button.setText("Zakończ edycję")

            # Przechowuj aktualne wartości dla każdego wiersza w kolumnie "Produkt"
            for row in range(self.table_widget.table.rowCount()):
                current_item = self.table_widget.table.item(row, 0)
                current_values.append(current_item.text() if current_item else "")

                # Ustaw rozwijaną listę dla produktu dla każdego wiersza
                self.set_dropdown_for_product(row, current_values[row])

        # Jeśli tabela jest edytowalna, uczyn ją nieedytowalną
        else:
            self.table_widget.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.edit_button.setText("Edytuj")
            for row in range(self.table_widget.table.rowCount()):
                combo = self.table_widget.table.cellWidget(row, 0)
                if combo:
                    # Zapisz wartość wybraną z QComboBox jako element tabeli
                    current_text = combo.currentText()
                    self.table_widget.table.setItem(row, 0, QTableWidgetItem(current_text))
                    # Usuń QComboBox
                    self.table_widget.table.removeCellWidget(row, 0)

    def set_dropdown_for_product(self, row, current_value):
        combobox = QComboBox()
        product_list = self.get_product_list_from_db()
        combobox.addItems(product_list)

        # Uczyń QComboBox edytowalnym
        combobox.setEditable(True)

        # Dodaj QCompleter dla QComboBox
        completer = QCompleter(product_list)
        combobox.setCompleter(completer)

        # Ustaw bieżącą wartość na wcześniej wybraną
        combobox.setCurrentText(current_value)

        combobox.currentIndexChanged.connect(lambda: self.update_table_item(row, combobox))
        self.table_widget.table.setCellWidget(row, 0, combobox)

    def get_product_list_from_db(self):
        mycursor = mydb.cursor()
        mycursor.execute("SELECT NazwaProduktu FROM Produkty")
        result = mycursor.fetchall()
        return [item[0] for item in result]

    def save_changes_to_database(self):
        # Przygotuj kolumny do aktualizacji
        produkt_columns = [f"Produkt{i}" for i in range(1, 16)]  # lista produkt1 itd (numeracja w tej tabeli chyba)
        ilosc_columns = [f"Ilosc{i}" for i in range(1, 16)]

        # Odczytaj dane z tabeli i przygotuj dane do aktualizacji
        update_data = []
        for row in range(self.table_widget.table.rowCount()):
            produkt_item = self.table_widget.table.cellWidget(row, 0)  # produkty w kolumnie 0 (cellWidget)
            ilosc_item = self.table_widget.table.item(row, 1)  # ilosci w kolumnie 1
            # Odczytaj wartość z QComboBox
            prod = produkt_item.currentText() if produkt_item and produkt_item.currentText() != "" else None
            il = ilosc_item.text() if ilosc_item and ilosc_item.text() != "" else None
            il = None if il == "-----" else il
            # print(f"Produkt z QComboBox: {produkt_item.currentText() if produkt_item else 'Brak produkt_item'}")
            # print(f"Ilość z QTableWidgetItem: {ilosc_item.text() if ilosc_item else 'Brak ilosc_item'}")
            # print(f"Przypisane wartości - prod: {prod}, il: {il}")

            if prod is None or self.product_exists_in_db(prod):
                update_data.append((prod, il, produkt_columns[row], ilosc_columns[row]))

        # Aktualizuj bazę danych
        mycursor = mydb.cursor()
        for prod, il, prod_col, ilosc_col in update_data:
            try:
                sql = f"UPDATE {self.shop_name}_z SET {prod_col} = %s, {ilosc_col} = %s WHERE Data = %s"
                mycursor.execute(sql, (prod, il, self.date))
                mydb.commit()
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas aktualizacji bazy danych: {e}")
                return  # Return early if there's an error

        QMessageBox.information(self, "Sukces", "Zaktualizowano dane w bazie danych")

        # dodawanie do PodsumowanieKosztow
        laczny_zwrot = 0

        for prod, il, prod_col, ilosc_col in update_data:
            mycursor = mydb.cursor()
            sql = f"SELECT Cena FROM Produkty WHERE NazwaProduktu = %s"
            mycursor.execute(sql, (prod,))  # cause we have to have at least tuple
            result = mycursor.fetchall()
            price = result[0][0]  # Assuming price is the first field in the first row

            il = float(il)
            price = float(price)

            przychod = price * il
            laczny_zwrot += przychod

        laczny_zwrot = round(laczny_zwrot, 2)

        #print('to jest laczny zwrot: ', laczny_zwrot)

        mycursor = mydb.cursor()
        sql = f"SELECT Zwrot FROM PodsumowanieKosztow WHERE Data = %s and NazwaSklepu = %s"
        mycursor.execute(sql, (self.date, self.shop_name))
        wiersz_istnieje = mycursor.fetchall()

        if wiersz_istnieje:
            mycursor = mydb.cursor()
            sql = "UPDATE PodsumowanieKosztow SET Zwrot = %s WHERE Data = %s and NazwaSklepu = %s"
            mycursor.execute(sql, (laczny_zwrot, self.date, self.shop_name))
            mydb.commit()
            #print("istnieje")
        else:
            mycursor = mydb.cursor()
            sql = "INSERT INTO PodsumowanieKosztow (Data, NazwaSklepu, Zwrot) VALUES (%s, %s, %s)"
            val = (self.date, self.shop_name, laczny_zwrot)
            mycursor.execute(sql, val)
            mydb.commit()
            #print("stworze nowy wiersz")

    # def save_to_przychod_podsumowaniekosztow(self):
    def update_table_item(self, row, combobox):  # Nowa metoda
        self.table_widget.table.setItem(row, 0, QTableWidgetItem(combobox.currentText()))

    def product_exists_in_db(self, product_name):
        '''sprawdzamy czy produkt w ogole sie znajduje w tej tabeli produkty bo kod sam jakos nie wiem czemu
        nam nie aktualizuje tej tabeli jak jest None, nie wiem może nie przyjmuje NULL jako sama ta baza danych
        i jest problem zeby jako produkt dac wartosc null, nie da sie jak jest ten klucz obcy'''
        mycursor = mydb.cursor()
        query = "SELECT COUNT(*) FROM produkty WHERE NazwaProduktu = %s"
        mycursor.execute(query, (product_name,))
        result = mycursor.fetchone()
        return result[0] > 0


class TableWidget(QWidget):
    def __init__(self, df, parent=None):
        super(TableWidget, self).__init__(parent)
        self.df = df
        self.initUi()

    def initUi(self):
        layout = QVBoxLayout()

        # Create a table
        self.table = QTableWidget()

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set the number of columns
        self.table.setColumnCount(len(self.df.columns))

        # Set the column names
        self.table.setHorizontalHeaderLabels(self.df.columns)

        # Add rows to the table
        for row_number, (index, row_data) in enumerate(self.df.iterrows()):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        layout.addWidget(self.table)
        self.setLayout(layout)


class AddRecipientWidget(QWidget):
    """
    Klasa służy dodaniu nowego odbiorcy w bazie
    Zmienne z set placeholder tekst sa tymczasowe i pokazują odnośne jakiej zmiennej jest poszczególny formularz
    layout.addWidget z poszczególną nazwą inputu dodaje linijkę w której dodajemy nowe wartości do rekordu
    QLineEdit() - jest funkcją która pozwala na edycję danego wiersza
    """

    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app

        layout = QVBoxLayout()

        self.shop_name_input = QLineEdit()
        self.shop_name_input.setPlaceholderText("Nazwa sklepu")
        layout.addWidget(self.shop_name_input)

        self.short_name_input = QLineEdit()
        self.short_name_input.setPlaceholderText("Skrócona nazwa sklepu")
        layout.addWidget(self.short_name_input)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Miasto")
        layout.addWidget(self.city_input)

        self.street_input = QLineEdit()
        self.street_input.setPlaceholderText("Ulica")
        layout.addWidget(self.street_input)

        self.street_num_input = QLineEdit()
        self.street_num_input.setPlaceholderText("Numer budynku")
        layout.addWidget(self.street_num_input)

        self.postcode_input = QLineEdit()
        self.postcode_input.setPlaceholderText("Kod pocztowy")
        layout.addWidget(self.postcode_input)

        self.nip_input = QLineEdit()
        self.nip_input.setPlaceholderText("NIP")
        layout.addWidget(self.nip_input)

        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText("Rabat")
        layout.addWidget(self.discount_input)

        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_recipient)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def reset_form(self):
        """
        This function clears all the QLineEdit fields in the form.
        """
        self.shop_name_input.clear()
        self.short_name_input.clear()
        self.city_input.clear()
        self.street_input.clear()
        self.street_num_input.clear()
        self.postcode_input.clear()
        self.nip_input.clear()
        self.discount_input.clear()

    def add_recipient(self):
        """
        Funckja służy dodaniu zedytowanych elementów do bazy danych, wartości z _input.text() przypisywane są
        korzystając z cursora oraz komendy sql INSERT INTO dodając do poszczególnych
        """
        shop_name = self.shop_name_input.text()
        short_name = self.short_name_input.text()
        city = self.city_input.text()
        street = self.street_input.text()
        street_num = self.street_num_input.text()
        postcode = self.postcode_input.text()
        nip = self.nip_input.text()
        discount = self.discount_input.text() or "0"

        # Create the message box
        msg = QMessageBox()
        msg.setWindowTitle("Potwierdzenie danych")
        msg.setText(f"Zostaną dodane następujące dane:\n"
                    f"Nazwa sklepu: {shop_name}\n"
                    f"Skrócona nazwa sklepu: {short_name}\n"
                    f"Miasto: {city}\n"
                    f"Ulica: {street}\n"
                    f"Numer domu: {street_num}\n"
                    f"Kod pocztowy: {postcode}\n"
                    f"NIP: {nip}\n"
                    f"Stały rabat: {discount}\n"
                    f"Czy są poprawne?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Tak")
        msg.button(QMessageBox.No).setText("Nie")
        result = msg.exec_()

        if result == QMessageBox.Yes:
            mycursor = mydb.cursor()
            try:
                sql = "INSERT INTO odbiorcy (NazwaSklepu, SkroconaNazwa, Miasto, Ulica, NumerBudynku, KodPocztowy, NIP, StalyRabat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                val = (shop_name, short_name, city, street, street_num, postcode, nip, discount)
                mycursor.execute(sql, val)

                mydb.commit()

                QMessageBox.information(self, "Sukces", "Dodano nowego odbiorcę")

                # Clear the form
                self.reset_form()

                # Refresh the database view
                self.main_app.database_widget.refresh()

                # Switch back to the database widget
                self.main_app.show_database_widget()

                # Go back to the previous view
                self.main_app.go_back()
                self.main_app.go_back()

            finally:
                mycursor.close()


class UpdateRecipientWidget(AddRecipientWidget):
    def __init__(self, main_app, selected_data, parent=None):
        super().__init__(main_app, parent)
        self.selected_data = selected_data
        self.shop_name_input.setText(self.selected_data[1])
        self.shop_name_input.setReadOnly(True)
        self.short_name_input.setText(self.selected_data[2])
        self.city_input.setText(self.selected_data[3])
        self.street_input.setText(self.selected_data[4])
        self.street_num_input.setText(self.selected_data[5])
        self.postcode_input.setText(self.selected_data[6])
        self.nip_input.setText(self.selected_data[7])
        self.discount_input.setText(self.selected_data[8])
        self.add_button.setText("Zaktualizuj")

        # Disconnect any previous connections to the add_button
        try:
            self.add_button.clicked.disconnect()
        except TypeError:
            # This will be raised if there are no connections, in which case we can ignore it
            pass

        self.add_button.clicked.connect(self.update_recipient)
        # Add a delete button
        self.delete_button = QPushButton("Usuń")
        self.layout().addWidget(self.delete_button)
        self.delete_button.clicked.connect(self.delete_recipient)

    def update_recipient(self):
        shop_name = self.shop_name_input.text()
        short_name = self.short_name_input.text()
        city = self.city_input.text()
        street = self.street_input.text()
        street_num = self.street_num_input.text()
        postcode = self.postcode_input.text()
        nip = self.nip_input.text()
        discount = self.discount_input.text() or "0"

        # Create a cursor
        mycursor = mydb.cursor()

        try:
            sql = """
                UPDATE Odbiorcy
                SET NazwaSklepu = %s, 
                    SkroconaNazwa = %s, 
                    Miasto = %s,
                    Ulica = %s,
                    NumerBudynku = %s,
                    KodPocztowy = %s,
                    NIP = %s,
                    StalyRabat = %s
                WHERE ID = %s
                """

            val = (shop_name, short_name, city, street, street_num, postcode, nip, discount,self.selected_data[0])  # Using ID in the WHERE clause
            print(f"Updating recipient with ID {self.selected_data[0]}")
            mycursor.execute(sql, val)
            mydb.commit()

            QMessageBox.information(self, "Sukces", "Zaktualizowano dane odbiorcy")

            # Refresh the database view
            self.main_app.database_widget.refresh()

            # Switch back to the database widget
            self.main_app.show_database_widget()

            # Get back to original database view
            self.main_app.go_back()
            self.main_app.go_back()

        finally:
            mycursor.close()

    def delete_recipient(self):
        # Create a message box
        msg = QMessageBox()
        msg.setWindowTitle("Potwierdzenie usunięcia")
        msg.setText(f"Czy na pewno chcesz usunąć odbiorcę: {self.shop_name_input.text()}?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Tak")
        msg.button(QMessageBox.No).setText("Nie")
        result = msg.exec_()

        # Proceed with deletion only if "Yes" was clicked
        if result == QMessageBox.Yes:
            mycursor = mydb.cursor()

            try:
                sql = """
                    DELETE FROM Odbiorcy
                    WHERE ID = %s
                    """

                val = (self.selected_data[0],)  # Assuming ID is at index 0 in selected_data
                print(f"Deleting recipient with ID {self.selected_data[0]}")
                mycursor.execute(sql, val)
                mydb.commit()

                QMessageBox.information(self, "Sukces", "Usunięto odbiorcę")

                # Refresh the database view
                self.main_app.database_widget.refresh()

                # Switch back to the database widget
                self.main_app.show_database_widget()

            finally:
                mycursor.close()


class ShopNameDatabase(QWidget):
    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app

        layout = QVBoxLayout()

        mycursor = mydb.cursor()

        # Execute a query to the database
        mycursor.execute("SELECT NazwaSklepu FROM Odbiorcy")

        # Fetch all rows from the result of the query
        myresult = mycursor.fetchall()

        # Create a table
        self.table = QTableWidget()

        # Disallow editing of the table
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set the number of columns
        self.table.setColumnCount(3)
        # Set the column names
        self.table.setHorizontalHeaderLabels(["NazwaSklepu", "Przychody", "Zwroty"])

        # Add rows to the table
        for row_number, row_data in enumerate(myresult):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            button = QPushButton('Przychody')
            button.clicked.connect(lambda checked, row_number=row_number: self.show_incomes_def(row_number))
            self.table.setCellWidget(row_number, 1, button)

            # Add a button to the last column
            button = QPushButton('Zwroty')
            button.clicked.connect(lambda checked, row_number=row_number: self.show_returns_def(row_number))
            self.table.setCellWidget(row_number, 2, button)  # 2 is the index of the last column

        layout.addWidget(self.table)
        self.setLayout(layout)

    def show_incomes_def(self, row_number):
        shop_name = self.table.item(row_number, 0).text()  # 0 is the column number for "NazwaSklepu"
        date = self.main_app.get_selected_date()
        date_python = date.toPyDate()  # to bedzie teraz w typie ktore mozna przekazac jako select do sql
        self.main_app.show_incomes(shop_name, date_python)

    def show_returns_def(self, row_number):
        # Here, replace this with the function in the parent class that shows the new widget you want
        # You may need to pass the row_number or other parameters to that function
        shop_name = self.table.item(row_number, 0).text()
        date = self.main_app.get_selected_date()
        date_python = date.toPyDate()
        # Stworzenie kursora
        mycursor = mydb.cursor()

        # Zapytanie do bazy danych, aby sprawdzić, czy dla wybranej daty i sklepu jest ustawiony przychód
        query = "SELECT COUNT(*) FROM PodsumowanieKosztow WHERE Data = %s AND NazwaSklepu = %s AND Przychod IS NOT NULL"
        mycursor.execute(query, (date_python, shop_name))

        # Odczytanie wyniku - jeżeli liczba wierszy jest większa od 0, to znaczy że przychód jest ustawiony
        count = mycursor.fetchone()[0]

        if count > 0:
            self.main_app.show_returns(shop_name, date_python)
        else:
            QMessageBox.warning(self, 'Brak danych', 'Uzupełnij tabelę przychodów przed ustawianiem zwrotów.')


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.navigation_history = []  # List used as stack to track navigation history
        # self.chosen_date = QDate

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)

        # Ustaw język kalendarza na polski
        polish_locale = QLocale(QLocale.Polish, QLocale.Poland)
        self.calendar.setLocale(polish_locale)

        date = QDate.currentDate()
        self.calendar.setSelectedDate(date)

        # Umieść kalendarz w QGroupBox
        calendar_group = QGroupBox()
        calendar_layout = QVBoxLayout()  # do organizowania widzetow wewnatrz qgroupbox
        calendar_layout.addWidget(self.calendar)
        calendar_group.setLayout(calendar_layout)
        calendar_group.setFixedSize(600, 600)  # Ustawienie stałego rozmiaru QGroupBox na 500x400 pikseli

        self.menu = MainMenu(self)
        self.new_widget = NewWidget()
        self.database_widget = DatabaseWidget(self,
                                              self)  # Create new widget, because of parent=none and we use def from myapp
        self.add_recipient_widget = AddRecipientWidget(self)  # Dodajemy nowego odbiorcę
        self.add_product_widget = AddProductWidget(self)
        self.products_database_widget = ProductsDatabaseWidget(self, self)
        self.show_shops = ShopNameDatabase(self)
        self.all_database_widget = AllDatabaseWidget(self, self)
        self.daily_database_widget = DailyDatabaseWidget(self, self)
        self.show_income = Income(self)  # pass self (which is an instance of MyApp) to Income
        self.show_return = Return(self)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(calendar_group)  # Dodajemy calendar_group do stacked layout (1wszy widzet)
        self.stacked_layout.addWidget(self.menu)  # (drugi wizdet)
        self.stacked_layout.addWidget(self.new_widget)
        self.stacked_layout.addWidget(self.database_widget)
        self.stacked_layout.addWidget(self.add_recipient_widget)  # Dodajemy widget z dodawaniem odbiorcy
        self.stacked_layout.addWidget(self.show_shops)
        self.stacked_layout.addWidget(self.show_income)
        self.stacked_layout.addWidget(self.show_return)
        self.stacked_layout.addWidget(self.products_database_widget)
        self.stacked_layout.addWidget(self.add_product_widget)
        self.stacked_layout.addWidget(self.all_database_widget)
        self.stacked_layout.addWidget(self.daily_database_widget)

        container = QWidget()
        container.setLayout(self.stacked_layout)

        self.back_button = QPushButton('Wstecz')
        self.back_button.clicked.connect(self.go_back)
        self.back_button.hide()  # ukrycie przycisku na poczatku

        self.confirm_date_button = QPushButton('Potwierdź datę')  # New button to confirm date
        self.confirm_date_button.clicked.connect(self.ask_date_confirmation)

        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        main_layout.addWidget(self.back_button)
        main_layout.addWidget(self.confirm_date_button)  # Add the new button to layout

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        self.calendar.selectionChanged.connect(self.ask_date_confirmation)

    def go_back(self):
        print(self.navigation_history)
        if self.navigation_history:
            self.navigation_history.pop()  # Remove current widget from history
            if self.navigation_history:
                # If there are any widgets left in history, go back to the last one
                self.stacked_layout.setCurrentIndex(self.navigation_history[-1])
            else:
                # If no widgets left in history, show the calendar
                self.show_calendar()

    def ask_date_confirmation(self):
        selected_date = self.calendar.selectedDate()
        # self.chosen_date = selected_date
        msg = QMessageBox()
        msg.setWindowTitle("Potwierdzenie daty")
        msg.setText(f"Wybrana data to: {selected_date.toString('dd.MM.yyyy')}. Czy jest poprawna?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Tak")
        msg.button(QMessageBox.No).setText("Nie")
        result = msg.exec_()

        if result == QMessageBox.Yes:
            self.show_main_menu()

    def get_selected_date(self):
        return self.calendar.selectedDate()

    def show_calendar(self):
        self.navigation_history.append(0)  # Add calendar to navigation history
        self.stacked_layout.setCurrentIndex(0)
        self.back_button.hide()
        self.confirm_date_button.show()

    def show_main_menu(self):
        self.navigation_history.append(1)
        self.stacked_layout.setCurrentIndex(1)  # menu jest na 1 miejscu w tym staku
        self.back_button.show()
        self.confirm_date_button.hide()  # Hide the confirm date button when switch to the main menu

    def show_new_widget(self):
        self.navigation_history.append(2)
        self.stacked_layout.setCurrentIndex(2)
        self.back_button.show()

    def show_database_widget(self):
        self.navigation_history.append(3)
        self.stacked_layout.setCurrentIndex(3)  # Set new widget as current
        self.back_button.show()

    def show_add_recipient_widget(self):
        """
        Funkcja obsługująca dodanie nowego odbiorcy
        """
        self.navigation_history.append(4)
        self.stacked_layout.setCurrentIndex(4)  # Set new widget as current
        self.back_button.show()

    def show_products_database_widget(self):
        self.navigation_history.append(8)
        self.stacked_layout.setCurrentIndex(8)
        self.back_button.show()

    def show_add_product_widget(self):
        self.navigation_history.append(9)
        self.stacked_layout.setCurrentIndex(9)  # Set new widget as current
        self.back_button.show()

    def show_all_database_widget(self):
        self.navigation_history.append(10)
        self.stacked_layout.setCurrentIndex(10)
        self.back_button.show()

    def show_daily_database_widget(self):
        self.navigation_history.append(11)
        self.stacked_layout.setCurrentIndex(11)
        self.back_button.show()

    def show_update_recipient_widget(self, selected_data):
        self.update_recipient_widget = UpdateRecipientWidget(self, selected_data)
        self.stacked_layout.addWidget(self.update_recipient_widget)
        self.navigation_history.append(self.stacked_layout.count() - 1)
        self.stacked_layout.setCurrentIndex(self.navigation_history[-1])
        self.back_button.show()

    def show_shop_name_database(self):
        self.navigation_history.append(5)
        self.stacked_layout.setCurrentIndex(5)  # Set new widget as current
        self.back_button.show()

    def show_incomes(self, shop_name, date):
        self.show_income.update_shop_name_and_date(shop_name, date)
        self.stacked_layout.setCurrentIndex(6)
        self.navigation_history.append(6)
        self.back_button.show()

    # Do the same for show_returns

    def show_returns(self, shop_name, date):
        self.show_return.update_shop_name_and_date(shop_name, date)
        self.navigation_history.append(7)
        self.stacked_layout.setCurrentIndex(7)  # Set new widget as current
        self.back_button.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyApp()
    window.resize(800, 900)
    window.show()

    sys.exit(app.exec_())
