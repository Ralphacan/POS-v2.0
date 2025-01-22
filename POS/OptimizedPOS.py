import sqlite3
import DbFunctions
from sys import exit, argv
import plotly.express as px
from CompleteSale import SaleWin
from collections import defaultdict
from DebtsCredits import CreditWindow
from FloatExpenses import FloatWindow
from StockAddition import StockWindow
from datetime import datetime, timedelta
from pandas import DataFrame, to_datetime
from ReportGeneration import ReportWindow
from TransactionHistory import TransactionWindow
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent, QObject
from PyQt5.QtWidgets import (QApplication, QWidget, QFrame, QMainWindow, QLabel, QHBoxLayout, QLineEdit, QAction,
                             QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QMessageBox, QVBoxLayout,
                             QSpacerItem, QSizePolicy, QAbstractItemView, QInputDialog, QToolButton, QDialog)


# noinspection PyUnresolvedReferences
def get_formatted_datetime():
    now = datetime.now()
    return now.strftime("%A %B %d %Y\n%H:%M %p")


def search_table(searchWidget, tableWidget):
    """Filter table rows based on search input."""
    search_text = searchWidget.text().lower()

    # Loop through table rows and hide those that do not match the search
    for row_ in range(tableWidget.rowCount()):
        match = False
        for col_ in range(tableWidget.columnCount()):
            item_ = tableWidget.item(row_, col_)
            if item_ and search_text in item_.text().lower():
                match = True
                break  # If one item in the row matches, no need to check other columns
        tableWidget.setRowHidden(row_, not match)


def qTool_button(imgPath, x, y):
    button = QToolButton()
    original_pixmap = QPixmap(imgPath)
    scaled_pixmap = original_pixmap.scaled(x, y, aspectRatioMode=Qt.KeepAspectRatio)
    button.setIcon(QIcon(scaled_pixmap))
    button.setIconSize(scaled_pixmap.size())

    return button


class HoverEventEater(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            target_widget = obj.findChild(QWidget, "tableWidget")
            icon_widget = obj.findChild(QWidget, "imgFrame")
            icon_widget.setVisible(False)
            target_widget.setVisible(True)
            return True
        elif event.type() == QEvent.Leave:
            target_widget = obj.findChild(QWidget, "tableWidget")
            icon_widget = obj.findChild(QWidget, "imgFrame")
            target_widget.setVisible(False)
            icon_widget.setVisible(True)
            return True
        return QObject.eventFilter(self, obj, event)


class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.companyName = "{} POS".format("Hudumia Cyber")

        self.headerBar = QFrame()
        self.contentSection = QFrame()
        self.footerBar = QFrame()

        self.cart_widget = None
        self.stock_widget = None
        self.non_quantifiable_items = []
        self.stock_data = None

        self.tableView_frame = QWidget()
        self.categoryView_frame = QWidget()

        self.header_style = """
                            QHeaderView::section {
                                background-color: #6c7ae0;
                                color: #fff;
                                padding: 2px;
                                font-size: 15px;
                                font-weight: bold;
                                border-width: 0px 0px 0px 0px;
                                border-style: dotted;
                            }
                        """

        self.cell_style = """            
                                    QTableWidget::item {
                                        padding-left: 15px;
                                        border-width: 0px 0px 1px 0px;
                                        border-style: solid;
                                        border-color: #666;
                                    }

                                    QTableWidget::item:Selected {
                                        color: #000;
                                        background-color: lightblue;
                                    }

                                    QTableWidget {
                                        background-color: white;   
                                    }
                                """

        self.totalLabel = QLabel("0.00")
        self.totalLabel.setStyleSheet("font-size: 80px;")
        self.transaction_no = QLabel()
        self.date_time_label = QLabel()
        self.date_time_label.setStyleSheet("font-size: 15px;"
                                          "color: #fff;")
        self.database_initialization()
        self.window_setup()

    def update_date_time(self):
        self.date_time_label.setText(get_formatted_datetime())

    def database_initialization(self):
        """Collects all initial pre database data"""
        try:
            dbPath = "assets/files/main.db"
            last_transaction = DbFunctions.database_all_lookup(db_path=dbPath, what_selection="transaction_code",
                                                               from_selection="Transactions")

            db_connection = sqlite3.connect(dbPath)
            cursor = db_connection.cursor()

            # Query to join stocks with products, and fetch quantifiable information
            cursor.execute("""
                SELECT Stock.stock_id, Stock.quantity, Products.product_id, Products.product_name, 
                       Products.base_price, Products.quantifiable
                FROM Products
                LEFT JOIN Stock ON Stock.stock_id = Products.stock_id
            """)

            # Dictionary to store stock data, with "miscellaneous" for non-quantifiable items
            stock_data = defaultdict(lambda: {'quantity': 0, 'products': []})

            for stock_id, quantity, product_id, product_name, price, quantifiable in cursor.fetchall():
                if quantifiable.lower() == "yes":
                    # For quantifiable items (products), store in stock_data by stock_id
                    stock_data[stock_id]['quantity'] = quantity
                    stock_data[stock_id]['products'].append({
                        'product_id': product_id,
                        'product_name': product_name,
                        'price': price
                    })
                else:
                    # For non-quantifiable items (services), add to "miscellaneous"
                    stock_data['Service']['products'].append({
                        'product_id': product_id,
                        'product_name': product_name,
                        'price': price
                    })
                    self.non_quantifiable_items.append(product_id)  # Add to separate list for easy access

            # Close the database connection
            db_connection.close()
            self.stock_data = stock_data

            if last_transaction:
                lasT_code = str(last_transaction[-1]).replace("('", "").replace("',)", "")

                if int(lasT_code[8:]) + 1 <= 9999:
                    new_code = lasT_code[:8] + str(int(lasT_code[8:]) + 1).zfill(4)
                    self.transaction_no.setText(new_code)

                else:
                    new_code = "HDC " + str(int(lasT_code[4:7]) + 1).zfill(3) + '/0001'
                    self.transaction_no.setText(new_code)

            else:
                self.transaction_no.setText("HDC 001/0001")

        except sqlite3.OperationalError:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)  # Set the icon to indicate an error
            msg_box.setWindowTitle("File Error!")  # Set the title of the message box
            msg_box.setText("Could not access database")  # Set the error message text
            msg_box.setStandardButtons(QMessageBox.Ok)  # Add an "Ok" button to close the box
            msg_box.exec_()

            raise KeyboardInterrupt

    def window_setup(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.headerBar = QFrame()
        self.headerBar.setFixedHeight(45)
        self.headerBar.setStyleSheet(f"background-color: #0A4395;")

        self.contentSection = QWidget()
        self.contentSection.setStyleSheet(f"background-color: #D6E7F5;")

        self.footerBar = QFrame()
        self.footerBar.setFixedHeight(70)
        self.footerBar.setStyleSheet(f"background-color: #0A4395;")

        main_layout.addWidget(self.headerBar)
        main_layout.addWidget(self.contentSection)
        main_layout.addWidget(self.footerBar)

        self.header_setup()
        self.content_setup()
        self.footer_setup()

    def header_setup(self):
        headerBar_layout = QHBoxLayout()
        headerBar_layout.setSpacing(0)
        headerBar_layout.setContentsMargins(0, 0, 5, 0)
        self.headerBar.setLayout(headerBar_layout)

        companyLabel = QLabel()
        companyLabel.setText(self.companyName.upper())
        companyLabel.setStyleSheet("font-size: 25px;"
                                   "color: white;"
                                   "font-weight: bold;")

        helpButton = qTool_button(imgPath="assets/images/help.png", x=30, y=30)
        helpButton.setStyleSheet("""
                QToolButton {
                    border: 0px solid white;
                    color: white;
                }

                QToolTip {
                    background-color: #f0f0f0;
                    color: #000;
                    border: 1px solid black;
                    margin: 0px;
                }
        """)
        helpButton.setToolTip("Help")

        headerBar_layout.setAlignment(Qt.AlignCenter)
        headerBar_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding))
        headerBar_layout.addWidget(companyLabel)
        headerBar_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding))
        headerBar_layout.addWidget(helpButton, alignment=Qt.AlignRight)

    def content_setup(self):
        content_layout = QHBoxLayout(self.contentSection)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)

        content_layout.addWidget(self.tableView_frame, stretch=2)
        content_layout.addWidget(self.categoryView_frame, stretch=1)

        self.table_view()
        self.category_view()

    def footer_setup(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_date_time)
        timer.start(60000)
        self.update_date_time()

        footerBar_layout = QHBoxLayout()
        footerBar_layout.setSpacing(15)
        footerBar_layout.setContentsMargins(15, 0, 15, 0)
        footerBar_layout.setAlignment(Qt.AlignLeft)
        self.footerBar.setLayout(footerBar_layout)

        footerButton_stylesheet = """
                QToolButton {
                    border: 0px solid white;
                    color: white;
                }

                QToolTip {
                    background-color: #f0f0f0;
                    color: #000;
                    border: 1px solid black;
                    margin: 0px;
                }
        """

        floatInput = qTool_button(imgPath="assets/images/floatError.png", x=35, y=35)
        floatInput.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        floatInput.setStyleSheet(footerButton_stylesheet)
        floatInput.setToolTip("Enter float\nCtrl+F")
        floatInput.setText(" Float")
        floatInput.setShortcut(QKeySequence("Ctrl+F"))
        floatInput.clicked.connect(lambda: FloatWindow(self))

        reportButton = qTool_button(imgPath="assets/images/report.png", x=35, y=35)
        reportButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        reportButton.setStyleSheet(footerButton_stylesheet)
        reportButton.setToolTip("Report Generation\nCtrl+R")
        reportButton.setText("Report")
        reportButton.setShortcut(QKeySequence("Ctrl+R"))
        reportButton.clicked.connect(lambda: ReportWindow(self))

        debtButton = qTool_button(imgPath="assets/images/overdue.png", x=35, y=35)
        debtButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        debtButton.setStyleSheet(footerButton_stylesheet)
        debtButton.setToolTip("Debt List\nCtrl+D")
        debtButton.setText("  Debt")
        debtButton.setShortcut(QKeySequence("Ctrl+D"))
        debtButton.clicked.connect(lambda: CreditWindow(self))

        stockButton = qTool_button(imgPath="assets/images/stockAdd.png", x=35, y=35)
        stockButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        stockButton.setStyleSheet(footerButton_stylesheet)
        stockButton.setToolTip("Add Stock\nCtrl+A")
        stockButton.setText(" Stocks")
        stockButton.setShortcut(QKeySequence("Ctrl+A"))
        stockButton.clicked.connect(lambda: StockWindow(self))

        transactionButton = qTool_button(imgPath="assets/images/transaction.png", x=35, y=35)
        transactionButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        transactionButton.setStyleSheet(footerButton_stylesheet)
        transactionButton.setToolTip("Sales transactions\nCtrl+T")
        transactionButton.setText("Transact")
        transactionButton.setShortcut(QKeySequence("Ctrl+T"))
        transactionButton.clicked.connect(lambda: TransactionWindow(self))

        footerBar_layout.addWidget(self.date_time_label)
        footerBar_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding))
        footerBar_layout.addWidget(reportButton)
        footerBar_layout.addWidget(transactionButton)
        footerBar_layout.addWidget(stockButton)
        footerBar_layout.addWidget(debtButton)
        footerBar_layout.addWidget(floatInput)

    def table_view(self):
        tableView_layout = QVBoxLayout(self.tableView_frame)
        tableView_layout.setContentsMargins(0, 0, 0, 0)
        tableView_layout.setSpacing(2)

        table_widget = QTableWidget()
        table_widget.setColumnCount(7)
        table_widget.verticalHeader().setVisible(False)
        table_widget.horizontalHeader().setStyleSheet(self.header_style)
        table_widget.horizontalHeader().setHighlightSections(False)
        table_widget.setStyleSheet(self.cell_style)
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setAlternatingRowColors(True)
        table_widget.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Item ID', 'Item Code', 'Stock ID', 'Item Description', 'Quantity', 'Price', 'Subtotal']
        table_widget.setHorizontalHeaderLabels(column_headers)

        # Set stretch last section to allow automatic adjustment
        table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table_widget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table_widget.verticalHeader().setDefaultSectionSize(30)

        table_widget.setMouseTracking(True)

        def return_quantity(data):
            item_code = data[1]
            item_quantity = int(data[4])

            for cart_row in range(self.stock_widget.rowCount()):
                cart_item_code = self.stock_widget.item(cart_row, 0).text()
                if cart_item_code == item_code and cart_item_code not in self.non_quantifiable_items:
                    current_stock = int(self.stock_widget.item(cart_row, 4).text())
                    new_stock = current_stock + item_quantity
                    _qty = QTableWidgetItem(str(new_stock))
                    self.stock_widget.setItem(cart_row, 4, _qty)
                    _qty.setFlags(_qty.flags() ^ Qt.ItemIsEditable)
                    break

                elif cart_item_code == item_code and cart_item_code in self.non_quantifiable_items:
                    break

        def edit_quantity(data):
            for row in range(table_widget.rowCount()):
                # Check if the row data matches the selected row's data
                row_values = [table_widget.item(row, col).text() for col in range(table_widget.columnCount())]

                if row_values == data:
                    cart_qty = int(data[4])
                    quantity, ok = QInputDialog.getInt(self, "Enter Quantity", "Quantity to remove:", 1, 1, cart_qty, 1)

                    if ok:
                        # Deduct the quantity from the stock
                        new_stock = cart_qty - quantity

                        if new_stock > 0:
                            for cart_row in range(table_widget.rowCount()):
                                cart_item_code = table_widget.item(cart_row, 1).text()
                                if cart_item_code == data[1]:
                                    current_subtotal = float(table_widget.item(cart_row, 6).text())
                                    new_subtotal = current_subtotal - (quantity * float(data[5]))

                                    _qty = QTableWidgetItem(str(new_stock))
                                    _sub = QTableWidgetItem(str(new_subtotal))

                                    table_widget.setItem(cart_row, 6, _sub)
                                    table_widget.setItem(cart_row, 4, _qty)

                                    _sub.setFlags(_qty.flags() ^ Qt.ItemIsEditable)
                                    _qty.setFlags(_qty.flags() ^ Qt.ItemIsEditable)

                                    conv_total = float(self.totalLabel.text().replace(",", ""))
                                    new_subtotal = round(conv_total - (quantity * float(data[5])), 2)
                                    new_subtotal = str("{:,}".format(new_subtotal))
                                    self.totalLabel.setText(new_subtotal)

                            for cart_row in range(self.stock_widget.rowCount()):
                                cart_item_code = self.stock_widget.item(cart_row, 0).text()
                                if cart_item_code == data[1] and cart_item_code not in self.non_quantifiable_items:
                                    current_stk = int(self.stock_widget.item(cart_row, 4).text())
                                    new_stk = current_stk + quantity
                                    _qty = QTableWidgetItem(str(new_stk))
                                    self.stock_widget.setItem(cart_row, 4, _qty)
                                    _qty.setFlags(_qty.flags() ^ Qt.ItemIsEditable)
                                    break

                                elif cart_item_code == data[1] and cart_item_code in self.non_quantifiable_items:
                                    break

                        else:
                            remove_item(data)
                            msg_box = QMessageBox()
                            msg_box.setIcon(QMessageBox.Information)  # Set the icon to indicate an error
                            msg_box.setWindowTitle("Edit Quantity")  # Set the title of the message box
                            msg_box.setText(f"{data[3]} Item removed!")
                            msg_box.setStandardButtons(QMessageBox.Ok)  # Add an "Ok" button to close the box
                            msg_box.exec_()
                    break

        def remove_item(data):
            for row in range(table_widget.rowCount()):
                # Check if the row data matches the selected row's data
                row_values = [table_widget.item(row, col).text() for col in range(table_widget.columnCount())]

                if row_values == data:
                    table_widget.removeRow(row)  # Remove the matched row
                    subtotal = float(data[6])
                    return_quantity(data)
                    conv_total = float(self.totalLabel.text().replace(",", ""))
                    new_subtotal = round(conv_total - subtotal, 2)
                    new_subtotal = str("{:,}".format(new_subtotal))
                    self.totalLabel.setText(new_subtotal)
                    break  # Exit loop once the row is removed

        def show_context_menu(pos):
            # Get the index of the item that was clicked
            index = table_widget.indexAt(pos)

            if index.isValid():
                row = index.row()
                row_data = []

                for _col in range(table_widget.columnCount()):
                    _item = table_widget.item(row, _col)
                    row_data.append(_item.text() if _item else "")

                # Create and show the context menu
                context_menu = QMenu(table_widget)
                context_menu.setStyleSheet("""
                    QMenu::item:selected {  /* Hover effect */
                        background-color: #0078D7;  /* Hover background color */
                        color: white;  /* Hover text color */
                    }
                """)

                edit_action = QAction(QIcon('assets/images/edit.png'), "Deduct Quantity", table_widget)
                edit_action.triggered.connect(lambda: edit_quantity(data=row_data))
                context_menu.addAction(edit_action)

                remove_action = QAction(QIcon('assets/images/remove.png'), "Remove Item", table_widget)
                remove_action.triggered.connect(lambda: remove_item(data=row_data))
                context_menu.addAction(remove_action)

                context_menu.exec_(table_widget.viewport().mapToGlobal(pos))

        # table_widget.cellClicked.connect(get_data)
        table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        table_widget.customContextMenuRequested.connect(show_context_menu)
        self.cart_widget = table_widget

        # Checkout system
        checkoutFrame = QFrame()
        checkoutFrame_layout = QVBoxLayout()
        checkoutFrame_layout.setContentsMargins(0, 0, 0, 0)
        checkoutFrame_layout.setSpacing(0)
        checkoutFrame.setLayout(checkoutFrame_layout)
        # checkoutFrame.setStyleSheet("border: 1px solid #000;")

        left_frame = QFrame()
        left_frame.setStyleSheet("border-bottom: 1px solid gray;")
        left_frameLayout = QHBoxLayout()
        left_frameLayout.setSpacing(30)
        left_frame.setLayout(left_frameLayout)
        left_frameLayout.setAlignment(Qt.AlignRight)

        total_label = QLabel("Total:")
        total_label.setStyleSheet("margin-top: 30px;"
                                  "font-size: 20px;"
                                  "border-bottom: 0px solid white;")
        self.totalLabel.setStyleSheet("font-size: 80px;"
                                      "border-bottom: 0px solid white;")

        transaction_frame = QFrame()
        transaction_frame.setStyleSheet("border-bottom: 0px solid white;")
        transaction_frameLayout = QVBoxLayout()
        transaction_frameLayout.setSpacing(0)
        transaction_frame.setLayout(transaction_frameLayout)
        t_label = QLabel("Transaction Nº:")
        t_label.setStyleSheet("border-bottom: 0px solid white;")
        self.transaction_no.setStyleSheet("font-size: 30px;"
                                            "color: #50A1E3;"
                                            "border-bottom: 0px solid white;")

        transaction_frameLayout.addWidget(t_label)
        transaction_frameLayout.addWidget(self.transaction_no)

        left_frameLayout.addWidget(transaction_frame)
        left_frameLayout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding))
        left_frameLayout.addWidget(total_label)
        left_frameLayout.addWidget(self.totalLabel)

        center_frame = QFrame()
        center_frameLayout = QHBoxLayout()
        center_frameLayout.setSpacing(15)

        center_frameLayout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding))

        checkOut = qTool_button(imgPath="assets/images/cart.png", x=55, y=55)
        checkOut.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        checkOut.setStyleSheet("""
                QToolButton {
                    border: 0px solid white;
                    color: #000;
                }

                QToolTip {
                    background-color: #f0f0f0;
                    color: #000;
                    border: 1px solid black;
                    margin: 0px;
                }
        """)
        checkOut.setToolTip("Checkout\nCtrl+C")
        checkOut.setText("   Complete Sale")
        checkOut.setShortcut(QKeySequence("Ctrl+C"))
        checkOut.clicked.connect(lambda: SaleWin(self, self.cart_widget, self.stock_data, self.totalLabel,
                                                 self.non_quantifiable_items, self.transaction_no))
        center_frameLayout.addWidget(checkOut)

        center_frameLayout.setAlignment(Qt.AlignRight)

        center_frame.setLayout(center_frameLayout)

        checkoutFrame_layout.addWidget(left_frame)
        checkoutFrame_layout.addWidget(center_frame)

        # ===================================================  Top Frame  ==============================================
        # ==============================================================================================================
        top_frame = QFrame()
        top_frame.setStyleSheet("background-color: white;"
                                "border: 1px solid #333;")
        topFrame_layout = QHBoxLayout()
        topFrame_layout.setContentsMargins(10, 3, 10, 3)
        top_frame.setLayout(topFrame_layout)

        search_input = QLineEdit()
        search_input.setStyleSheet("""
                   QLineEdit {
                       border: 1px solid gray;
                       border-bottom: 2px solid blue;
                       padding-left: 8px;
                       background-color: #F5F7FA;
                       color: #333;
                       font-size: 14px;
                   }
                   QLineEdit:hover {
                       border: 1px solid gray;
                       border-bottom: 2px solid #0056b3;
                       background-color: #EAF0F6;
                   }
                   QLineEdit:focus {
                       border-bottom: 2px solid blue;
                       background-color: #FFFFFF;
                       color: #333;
                   }
               """)
        icon_pixmap = QPixmap("assets/images/search.png").scaled(50, 50)
        search_icon = QIcon(icon_pixmap)

        search_action = QAction(search_icon, "", search_input)
        search_input.addAction(search_action, QLineEdit.LeadingPosition)
        search_input.setPlaceholderText("Search code, category, description...")
        search_input.setMaximumWidth(450)
        search_input.textChanged.connect(lambda: search_table(search_input, table_widget))

        def clear_cart():
            if table_widget.rowCount():
                for row in range(table_widget.rowCount()):
                    # Check if the row data matches the selected row's data
                    row_values = [table_widget.item(row, col).text() for col in range(table_widget.columnCount())]
                    return_quantity(row_values)

                table_widget.clearContents()
                table_widget.setRowCount(0)
                self.totalLabel.setText("0.00")

                msg_box = QMessageBox()
                msg_box.setWindowTitle("Table Items")
                msg_box.setText("Cart has been cleared successfully!")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Ok)
                QTimer.singleShot(1500, msg_box.close)
                msg_box.exec_()

        clearCart = qTool_button(imgPath="assets/images/shopping.png", x=30, y=30)
        clearCart.setStyleSheet("""
                QToolButton {
                    border: 0px solid white;
                    color: black;
                }

                QToolTip {
                    background-color: #f0f0f0;
                    color: #000;
                    border: 1px solid black;
                    margin: 0px;
                }
        """)
        clearCart.setToolTip("Clear Cart\nCtrl+Z")
        clearCart.setShortcut(QKeySequence("Ctrl+Z"))
        clearCart.clicked.connect(clear_cart)

        topFrame_layout.addWidget(search_input)
        topFrame_layout.addWidget(clearCart, alignment=Qt.AlignRight)

        tableView_layout.addWidget(top_frame, stretch=1)
        tableView_layout.addWidget(table_widget, stretch=10)
        tableView_layout.addWidget(checkoutFrame, stretch=5)

    def category_view(self):
        categoryView_layout = QVBoxLayout(self.categoryView_frame)
        categoryView_layout.setContentsMargins(2, 0, 2, 0)
        categoryView_layout.setSpacing(2)

        # ================================================== Top Section ===============================================
        def filter_by_category():
            """Filter the table rows based on the selected category."""
            selected_category = category_dropdown.currentText()

            # Loop through table rows and hide those that do not match the selected category
            for row in range(table_widget.rowCount()):
                item = table_widget.item(row, 1)  # Get the 'Category' column (index 1)
                if selected_category == "All (*)":
                    table_widget.setRowHidden(row, False)  # Show all rows
                elif item and item.text() != selected_category:
                    table_widget.setRowHidden(row, True)  # Hide rows that don't match the category
                else:
                    table_widget.setRowHidden(row, False)

        searchFrame = QFrame()
        searchFrame.setStyleSheet("border: 1px solid #000;"
                                  "background-color: white;")
        searchFrame_layout = QHBoxLayout()
        searchFrame.setLayout(searchFrame_layout)

        search_input = QLineEdit()
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid gray;
                border-bottom: 2px solid blue;
                padding-left: 8px;
                background-color: #F5F7FA;
                color: #333;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 1px solid gray;
                border-bottom: 2px solid #0056b3;
                background-color: #EAF0F6;
            }
            QLineEdit:focus {
                border-bottom: 2px solid blue;
                background-color: #FFFFFF;
                color: #333;
            }
        """)
        icon_pixmap = QPixmap("assets/images/search.png").scaled(50, 50)
        search_icon = QIcon(icon_pixmap)

        search_action = QAction(search_icon, "", search_input)
        search_input.addAction(search_action, QLineEdit.LeadingPosition)
        search_input.setPlaceholderText("Search code, stock id, name, price...")
        search_input.textChanged.connect(lambda: search_table(search_input, table_widget))
        searchFrame_layout.addWidget(search_input)

        category_dropdown = QComboBox()
        category_dropdown.setStyleSheet("""
            QComboBox {
                border: 1px solid #007BFF;
                background-color: #F5F7FA;
                color: #333;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #0056b3;
                background-color: #EAF0F6;
            }
            QComboBox::drop-down {
                border-left: 0px solid #007BFF;
                width: 25px;
                background-color: #F5F7FA;
            }
            QComboBox::down-arrow {
                image: url(assets/images/down.png); /* Path to custom down arrow icon */
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #007BFF;
                background-color: #FFFFFF;
                selection-background-color: #007BFF;
                selection-color: white;
                padding: 5px;
                color: #333;
            }
        """)
        category_dropdown.addItem("All (*)")  # Default option
        category_dropdown.currentIndexChanged.connect(filter_by_category)
        category_dropdown.setMinimumWidth(100)

        searchFrame_layout.addWidget(category_dropdown)

        # ================================== Designing the Categories Section ==========================================
        # ==============================================================================================================
        table_widget = QTableWidget()
        table_widget.verticalHeader().setVisible(False)
        table_widget.setShowGrid(False)
        table_widget.horizontalHeader().setStyleSheet(self.header_style)
        table_widget.horizontalHeader().setHighlightSections(False)
        table_widget.setStyleSheet(self.cell_style)
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setAlternatingRowColors(True)
        table_widget.setFocusPolicy(Qt.NoFocus)
        table_widget.setObjectName("tableWidget")

        column_headers = ['Code', 'Stock ID', 'Name', 'Price', 'InStock']
        table_widget.setColumnCount(len(column_headers))
        table_widget.setHorizontalHeaderLabels(column_headers)

        table_widget.setRowCount(sum(len(stock['products']) for stock in self.stock_data.values()))

        # Populate the table with stock and product data
        row = 0  # Start row counter
        for stock_id, stock_info in self.stock_data.items():
            stock_quantity = stock_info['quantity']  # Quantity of this stock

            for product in stock_info['products']:
                try:
                    # Assuming product['product_id'] as 'Code', and product_name as 'Name'
                    # Also assuming you have the category stored or can derive it; using a placeholder here

                    # Set values for each column
                    key_item = QTableWidgetItem(str(product['product_id']))  # Code
                    key_item.setFlags(key_item.flags() ^ Qt.ItemIsEditable)
                    table_widget.setItem(row, 0, key_item)

                    category_item = QTableWidgetItem(stock_id)  # Category (replace as needed)
                    category_item.setFlags(category_item.flags() ^ Qt.ItemIsEditable)
                    table_widget.setItem(row, 1, category_item)

                    name_item = QTableWidgetItem(product['product_name'])  # Name
                    name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
                    table_widget.setItem(row, 2, name_item)

                    price_item = QTableWidgetItem(f"{product['price']:.2f}")  # Price
                    price_item.setFlags(price_item.flags() ^ Qt.ItemIsEditable)
                    table_widget.setItem(row, 3, price_item)

                    stock_item = QTableWidgetItem(str(stock_quantity))  # Stock quantity
                    stock_item.setFlags(stock_item.flags() ^ Qt.ItemIsEditable)
                    table_widget.setItem(row, 4, stock_item)

                    # Increment row for the next product
                    row += 1

                except TypeError:
                    pass

        # Set stretch last section to allow automatic adjustment
        table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table_widget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table_widget.verticalHeader().setDefaultSectionSize(30)

        image_frame = QFrame()
        image_frame.setStyleSheet("border: 1px solid #000;"
                                  "background-color: white;")
        image_frame_layout = QVBoxLayout()
        image_frame.setLayout(image_frame_layout)
        image_frame.setObjectName("imgFrame")

        image_label = QLabel()
        image_label.setStyleSheet("border: 0px solid #000;")
        original_pixmap = QPixmap("eye.png")
        scaled_pixmap = original_pixmap.scaled(200, 100, aspectRatioMode=Qt.KeepAspectRatio)
        image_label.setPixmap(scaled_pixmap)
        image_frame_layout.addWidget(image_label)
        image_frame_layout.setAlignment(Qt.AlignCenter)

        categoryView_layout.addWidget(searchFrame, stretch=1)
        categoryView_layout.addWidget(table_widget, stretch=19)
        categoryView_layout.addWidget(image_frame, stretch=19)

        def populate_category_dropdown():
            """Populate the category dropdown with unique categories from the table widget."""
            categories = set()

            # Loop through all rows in the table
            for row in range(table_widget.rowCount()):
                # Get the item in the 'Category' column (index 1)
                category_item = table_widget.item(row, 1)
                if category_item:
                    categories.add(category_item.text())

            # Add unique categories to the dropdown
            for category in sorted(categories):
                category_dropdown.addItem(category)

        populate_category_dropdown()

        def handle_row_double_click(_row, _col):
            """Handle the double-click event and retrieve row data."""
            # Collect the row data
            row_data = []
            for _col in range(table_widget.columnCount()):
                _item = table_widget.item(_row, _col)
                row_data.append(_item.text() if _item else "")

            # Retrieve the stock value from the selected row (assuming stock is in column 4)
            stock_item_ = table_widget.item(_row, 4)  # Assuming stock is in column index 4
            max_stock = int(stock_item_.text()) if stock_item_ else 0

            # Ask for quantity input with the maximum set to the stock value
            if max_stock > 0 and table_widget.item(_row, 0).text() not in self.non_quantifiable_items:
                quantity, ok = QInputDialog.getInt(self, "Enter Quantity", "Quantity:", 1, 1, max_stock, 1)

                if ok:
                    # Deduct the quantity from the stock
                    new_stock = max_stock - quantity
                    stock_item_.setText(str(new_stock))  # Update the stock in the table
                    _price_item = table_widget.item(_row, 3)
                    price = float(_price_item.text()) if _price_item else 0

                    # Add the row data and quantity to the other table
                    add_to_cart(row_data, quantity, price)

            elif max_stock == 0 and table_widget.item(_row, 0).text() in self.non_quantifiable_items:
                quantity, ok = QInputDialog.getInt(self, "Enter Quantity", "Quantity:", 1, 1, 10000000, 1)

                if ok:
                    _price_item = table_widget.item(_row, 3)
                    price = float(_price_item.text()) if _price_item else 0

                    # Add the row data and quantity to the other table
                    add_to_cart(row_data, quantity, price)

            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)  # Set the icon to indicate an error
                msg_box.setWindowTitle("Stock Error!")  # Set the title of the message box
                msg_box.setText(f"{row_data[2]} stock has been depleted!\nAdd more stock!")
                msg_box.setStandardButtons(QMessageBox.Ok)  # Add an "Ok" button to close the box
                msg_box.exec_()

        def add_to_cart(row_data, quantity, basePrice):
            """Add the selected row to the cart or update the quantity if it already exists."""
            item_code = row_data[0]
            item_exists = False
            subtotal = quantity * basePrice

            # Loop through the cart to check if the item is already there
            for cart_row in range(self.cart_widget.rowCount()):
                cart_item_code = self.cart_widget.item(cart_row, 1).text()
                if cart_item_code == item_code:
                    # Update the quantity if item already exists
                    current_quantity = int(self.cart_widget.item(cart_row, 4).text())
                    current_subtotal = float(self.cart_widget.item(cart_row, 6).text())
                    new_quantity = current_quantity + quantity
                    new_subtotal = current_subtotal + subtotal

                    _qty = QTableWidgetItem(str(new_quantity))
                    _sub = QTableWidgetItem(str(new_subtotal))

                    self.cart_widget.setItem(cart_row, 4, _qty)
                    self.cart_widget.setItem(cart_row, 6, _sub)
                    item_exists = True
                    _qty.setFlags(_qty.flags() ^ Qt.ItemIsEditable)
                    _sub.setFlags(_sub.flags() ^ Qt.ItemIsEditable)

                    conv_total = float(self.totalLabel.text().replace(",", ""))

                    update_total = round(conv_total + subtotal, 2)
                    update_total = str("{:,}".format(update_total))
                    self.totalLabel.setText(update_total)
                    break

            # If the item does not exist in the cart, add it
            if not item_exists:
                row_position = self.cart_widget.rowCount()
                self.cart_widget.insertRow(row_position)
                row_data.insert(0, str(row_position))
                row_data.insert(4, str(quantity))
                row_data.insert(6, str(subtotal))
                row_data.pop(7)

                conv_total = float(self.totalLabel.text().replace(",", ""))
                update_total = round(conv_total + subtotal, 2)
                update_total = str("{:,}".format(update_total))
                self.totalLabel.setText(update_total)
                for _col_, _value in enumerate(row_data):
                    row_item = QTableWidgetItem(_value)
                    self.cart_widget.setItem(row_position, _col_, row_item)
                    row_item.setFlags(row_item.flags() ^ Qt.ItemIsEditable)

        table_widget.cellDoubleClicked.connect(handle_row_double_click)

        table_widget.setVisible(False)
        self.stock_widget = table_widget
        self.categoryView_frame.setMouseTracking(True)
        keyPressEater = HoverEventEater(self)
        self.categoryView_frame.installEventFilter(keyPressEater)

    def reports_generation(self):
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)

        def fetch_sales(period="Today", startDate=None, endDate=None):
            datePeriods = {
                "Today": (today_start, today_start + timedelta(days=1)),
                "Yesterday": (today_start - timedelta(days=1), today_start),
                "Last 3 Days": (today_start - timedelta(days=3), today_start + timedelta(days=1)),
                "Last Week": (today_start - timedelta(weeks=1), today_start + timedelta(days=1)),
                "Last Month": (today_start - timedelta(days=30), today_start + timedelta(days=1)),
                "Last 3 Months": (today_start - timedelta(days=90), today_start + timedelta(days=1)),
                "Last 6 Months": (today_start - timedelta(days=180), today_start + timedelta(days=1)),
                "Last 1 Year": (today_start - timedelta(days=365), today_start + timedelta(days=1))
            }

            if not startDate and not endDate:
                startDate, endDate = datePeriods[period]

                # Convert startDate and endDate to strings in SQLite-compatible format
                # ("%A, %B %d, %Y\n%I:%M %p")
                startDate_str = startDate.strftime('%Y-%m-%d %H:%M:%S')
                endDate_str = endDate.strftime('%Y-%m-%d %H:%M:%S')

                # SQL query to fetch records with transaction_date within the specified range
                query = f"""
                                SELECT * FROM Sales
                                WHERE strftime('%Y-%m-%d %H:%M:%S', transaction_date) >= ? 
                                  AND strftime('%Y-%m-%d %H:%M:%S', transaction_date) < ?
                            """

                # Connect to the database and execute the query
                conn = sqlite3.connect("assets/files/main.db")
                cursor = conn.cursor()
                cursor.execute(query, (startDate_str, endDate_str))

                # Fetch all matching records
                all_sales = cursor.fetchall()

                # Close the database connection
                conn.close()

                df = DataFrame(all_sales, columns=['transaction_id', 'transaction_date', 'description', 'unit_price',
                                                      'quantity', 'total'])

                # Convert transaction_date to datetime format
                df['transaction_date'] = to_datetime(df['transaction_date'], format='%Y-%m-%d %H:%M:%S')

                # Aggregate data based on the selected period
                if period in ["Today", "Yesterday"]:
                    df['time_period'] = df['transaction_date'].dt.hour  # Group by hour
                elif period in ["Last 3 Days", "Last Week", "Last Month"]:
                    df['time_period'] = df['transaction_date'].dt.date  # Group by day
                else:
                    df['time_period'] = df['transaction_date'].dt.to_period("W")  # Group by week

                # Group and sum totals
                grouped_data = df.groupby('time_period')['total'].sum().reset_index()
                grouped_data['time_period'] = grouped_data['time_period'].astype(str)  # Convert to string for plotting

                # Plot using Plotly
                fig = px.bar(grouped_data, x='time_period', y='total', title=f'Sales Data ({period})')
                fig.update_layout(xaxis_title="Time", yaxis_title="Total Sales")
                fig.show()

                return all_sales

        # print(fetch_sales(period="Last Week"))

        reports_window = QDialog(self)
        reports_window.setFixedSize(QSize(600, 600))
        reports_window.setWindowTitle("Generate Reports")
        reports_windowLayout = QVBoxLayout()
        reports_windowLayout.setSpacing(10)
        reports_window.setLayout(reports_windowLayout)

        selection_frame = QFrame()
        selection_frameLayout = QHBoxLayout()
        selection_frame.setLayout(selection_frameLayout)
        selection_frame.setStyleSheet("background-color: green;")

        sales_frame = QFrame()
        sales_frameLayout = QHBoxLayout()
        sales_frame.setLayout(sales_frameLayout)
        sales_frame.setStyleSheet("background-color: blue;")

        pie_chart = QFrame()
        pie_chartLayout = QHBoxLayout()
        pie_chart.setLayout(pie_chartLayout)
        pie_chart.setStyleSheet("background-color: yellow;")

        reports_windowLayout.addWidget(selection_frame, stretch=1)
        reports_windowLayout.addWidget(sales_frame, stretch=5)
        reports_windowLayout.addWidget(pie_chart, stretch=4)

        reports_window.exec_()

if __name__ == '__main__':
    app = QApplication(argv)

    try:
        main_window = AdminApp()
        main_window.setWindowTitle('POS Command Terminal')
        main_window.showMaximized()
        exit(app.exec_())

    except KeyboardInterrupt:
        app.quit()