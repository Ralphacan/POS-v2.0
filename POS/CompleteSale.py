import DbFunctions
from datetime import datetime
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QVBoxLayout,
                             QSpacerItem, QSizePolicy, QDialog, QCheckBox, QListWidget, QListWidgetItem, QPushButton)
        

class SaleWin:
    def __init__(self, Parent, CartWidget, StockData, TotalLabel, QItems, Tno):
        self.saleWin = None
        self.parent = Parent
        self.cart_widget = CartWidget
        self.stock_data = StockData
        self.totalLabel = TotalLabel
        self.non_quantifiable_items = QItems
        self.transaction_no = Tno
        
        self.productList = QListWidget()
        self.paymentFrame = QFrame()
        self.miniTable = QTableWidget()

        self.currentPayment = None
        self.dbPath = "assets/files/main.db"
        self.switchMode = None
        
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

        self.window_setup()
    
    def check_cart_quantities(self):
        cart_quantities_by_stock = {}

        # Step 1: Sum quantities in the cart by stock_id
        for row in range(self.cart_widget.rowCount()):
            # Retrieve product_id and quantity from the cart widget
            product_id = self.cart_widget.item(row, 1).text()  # Assuming product_id is in the first column
            quantity = int(self.cart_widget.item(row, 4).text())  # Assuming quantity is in the second column

            # Find the stock_id for the product in stock_data
            stock_id = None
            for s_id, stock_info in self.stock_data.items():
                for product in stock_info['products']:
                    if product['product_id'] == product_id:
                        stock_id = s_id
                        break
                if stock_id is not None:
                    break

            if stock_id is None:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Quantity Errors!")
                msg_box.setText(f"Product with ID {product_id} not found in stock.")
                msg_box.setIcon(QMessageBox.Warning)
                QTimer.singleShot(3000, msg_box.close)
                msg_box.exec_()
                return False

            # Add quantity to the relevant stock_id in cart_quantities_by_stock
            if stock_id not in cart_quantities_by_stock:
                cart_quantities_by_stock[stock_id] = 0
            cart_quantities_by_stock[stock_id] += quantity

        # Step 2: Compare cart quantities to available stock quantities
        for stock_id, total_quantity in cart_quantities_by_stock.items():
            available_quantity = self.stock_data[stock_id]['quantity']
            if total_quantity > available_quantity and stock_id != 'Service':
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Quantity Errors!")
                msg_box.setText(f"Insufficient stock for stock ID {stock_id}: required {total_quantity}, available "
                                f"{available_quantity}.")
                msg_box.setIcon(QMessageBox.Warning)
                QTimer.singleShot(3000, msg_box.close)
                msg_box.exec_()
                return False

            elif total_quantity > available_quantity and stock_id == 'Service':
                return True

        return True
    
    def window_setup(self):
        if self.cart_widget.rowCount() and self.check_cart_quantities():
            self.saleWin = QDialog(self.parent)
            self.saleWin.setFixedSize(QSize(800, 400))
            self.saleWin.setWindowTitle("Complete Transaction")
            saleWin_layout = QHBoxLayout()
            saleWin_layout.setSpacing(10)
            self.saleWin.setLayout(saleWin_layout)
            
            self.product_list_setup()
            self.payment_setup()

            saleWin_layout.addWidget(self.productList, stretch=1)
            saleWin_layout.addWidget(self.paymentFrame, stretch=1)

            self.saleWin.exec_()
            
        else:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Table Items")
            msg_box.setText("Sale cannot be completed, no transactions to record!")
            msg_box.setIcon(QMessageBox.Warning)
            QTimer.singleShot(1500, msg_box.close)
            msg_box.exec_()
            
    def product_list_setup(self):
        for row in range(self.cart_widget.rowCount()):
            # Check if the row data matches the selected row's data
            row_values = [self.cart_widget.item(row, col).text() for col in range(self.cart_widget.columnCount())]
            representation = (f"{row_values[1]}{row_values[1]}{row_values[1]} \t{row_values[3]}\n"
                              f"Qty: {row_values[4]} @ {row_values[5]} \tSubtotal: {row_values[6]}/=")
            item = QListWidgetItem(f"{representation}")
            self.productList.addItem(item)

        self.productList.setStyleSheet("""
                QListWidget {
                    font-size: 15px;
                    border: 2px solid #6c7ae0;
                }

                QListWidget::item {
                    border-bottom: 1px solid lightgray;
                    padding: 5px;
                }
        """)
        self.productList.setFocusPolicy(Qt.NoFocus)
        
    def payment_setup(self):
        paymentFrame_layout = QVBoxLayout()
        self.paymentFrame.setLayout(paymentFrame_layout)
        paymentFrame_layout.setContentsMargins(0, 0, 0, 0)

        checkBox_frame = QFrame()
        checkBox_frameLayout = QHBoxLayout()
        checkBox_frame.setLayout(checkBox_frameLayout)

        self.miniTable.setColumnCount(2)
        self.miniTable.verticalHeader().setVisible(False)
        self.miniTable.horizontalHeader().setStyleSheet(self.header_style)
        self.miniTable.horizontalHeader().setHighlightSections(False)
        self.miniTable.setStyleSheet(self.cell_style)
        self.miniTable.setAlternatingRowColors(True)
        self.miniTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.miniTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Description', 'Price']
        self.miniTable.setHorizontalHeaderLabels(column_headers)
        d = str(self.totalLabel.text()).replace(",", "")

        def get_column_values(column_index):
            values = []
            for row__ in range(self.cart_widget.rowCount()):
                item__ = self.cart_widget.item(row__, column_index)
                if item__ is not None:
                    values.append(int(item__.text()))
            return values

        miniTable_base = {
            'Total Amount Due': d + "/=",
            'Total items in cart': str(self.cart_widget.rowCount()),
            'Total Qty of items in cart': str(sum(get_column_values(4))),
            'Discount allowed in Amount': "0",
            'Amount Paid via Cash': d,
            'Amount Paid via Mpesa': "0"
        }

        self.miniTable.setRowCount(len(miniTable_base))

        # Populate the table with dummy data
        editable_rows = [3]  # Specify the rows that should have their last column editable (2nd row in this case)

        for row, (key, value) in enumerate(miniTable_base.items()):
            # Add the key as the first column
            key_item = QTableWidgetItem(str(key))
            key_item.setFlags(key_item.flags() ^ Qt.ItemIsEditable)
            self.miniTable.setItem(row, 0, key_item)

            # Insert the value in the next column (the last column in this case)
            item = QTableWidgetItem(str(value))

            # Check if this is the last column and if the row is editable
            if row in editable_rows:
                item.setFlags(item.flags() | Qt.ItemIsEditable)  # Allow editing
            else:
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # Disallow editing

            self.miniTable.setItem(row, 1, item)

        def update_cash_amount(editedItem):
            # Block the signal to prevent recursive calls
            total_amount = self.miniTable.item(0, 1)
            discountApplied = self.miniTable.item(3, 1)
            cash_amount = self.miniTable.item(4, 1)
            mpesa_amount = self.miniTable.item(5, 1)

            warning_box = QMessageBox()
            warning_box.setWindowTitle("Table Items")
            warning_box.setIcon(QMessageBox.Warning)

            self.miniTable.blockSignals(True)

            try:
                if editedItem.row() == 5 and self.currentPayment == "cash" and not self.switchMode:
                    try:
                        cash_amount.setFlags(cash_amount.flags() | Qt.ItemIsEditable)
                        mpesa_amount.setFlags(mpesa_amount.flags() | Qt.ItemIsEditable)
                        pre_amount = cash_amount.text()

                        newCash = (float(total_amount.text().replace("/=", "")) -
                                   float(discountApplied.text()) - float(mpesa_amount.text()))

                        if newCash >= 0:
                            cash_amount.setText(str(newCash))

                        else:
                            warning_box.setText(f"Cash Amount went negative {newCash}")
                            QTimer.singleShot(2000, warning_box.close)
                            warning_box.exec_()

                            discountApplied.setText("0")
                            mpesa_amount.setText("0")
                            cash_amount.setText(pre_amount)

                    except ValueError:
                        mpesa_amount.setText("0")
                        warning_box.setText("Values enter should be numbers!")
                        QTimer.singleShot(1500, warning_box.close)
                        warning_box.exec_()

                    finally:
                        cash_amount.setFlags(cash_amount.flags() ^ Qt.ItemIsEditable)

                elif editedItem.row() == 4 and self.currentPayment == "mpesa" and not self.switchMode:
                    try:
                        cash_amount.setFlags(cash_amount.flags() | Qt.ItemIsEditable)
                        mpesa_amount.setFlags(mpesa_amount.flags() | Qt.ItemIsEditable)
                        pre_amount = mpesa_amount.text()

                        newCash = (float(total_amount.text().replace("/=", "")) -
                                   float(discountApplied.text()) - float(cash_amount.text()))

                        if newCash >= 0:
                            mpesa_amount.setText(str(newCash))

                        else:
                            warning_box.setText(f"Mpesa Amount went negative {newCash}")
                            QTimer.singleShot(2000, warning_box.close)
                            warning_box.exec_()

                            discountApplied.setText("0")
                            cash_amount.setText("0")
                            mpesa_amount.setText(pre_amount)

                    except ValueError:
                        cash_amount.setText("0")
                        warning_box.setText("Values enter should be numbers!")
                        QTimer.singleShot(1500, warning_box.close)
                        warning_box.exec_()

                    finally:
                        mpesa_amount.setFlags(mpesa_amount.flags() ^ Qt.ItemIsEditable)

                elif editedItem.row() == 3 and self.currentPayment == "cash" and not self.switchMode:
                    try:
                        cash_amount.setFlags(cash_amount.flags() | Qt.ItemIsEditable)
                        mpesa_amount.setFlags(mpesa_amount.flags() | Qt.ItemIsEditable)

                        new_cash = (float(total_amount.text().replace("/=", "")) -
                                    float(mpesa_amount.text()) - float(discountApplied.text()))

                        if new_cash >= 0:
                            cash_amount.setText(str(new_cash))

                        else:
                            warning_box.setText(f"Cash Amount went negative {new_cash}")
                            QTimer.singleShot(2000, warning_box.close)
                            warning_box.exec_()

                            discountApplied.setText("0")
                            mpesa_amount.setText("0")
                            cash_amount.setText(total_amount.text().replace("/=", ""))

                    except ValueError:
                        discountApplied.setText("0")
                        warning_box.setText("Values enter should be numbers!")
                        QTimer.singleShot(1500, warning_box.close)
                        warning_box.exec_()

                    finally:
                        cash_amount.setFlags(cash_amount.flags() ^ Qt.ItemIsEditable)

                elif editedItem.row() == 3 and self.currentPayment == "mpesa" and not self.switchMode:
                    try:
                        cash_amount.setFlags(cash_amount.flags() | Qt.ItemIsEditable)
                        mpesa_amount.setFlags(mpesa_amount.flags() | Qt.ItemIsEditable)

                        new_cash = (float(total_amount.text().replace("/=", "")) -
                                    float(cash_amount.text()) - float(discountApplied.text()))

                        if new_cash >= 0:
                            mpesa_amount.setText(str(new_cash))

                        else:
                            warning_box.setText(f"Cash Amount went negative {new_cash}")
                            QTimer.singleShot(2000, warning_box.close)
                            warning_box.exec_()

                            discountApplied.setText("0")
                            cash_amount.setText("0")
                            mpesa_amount.setText(total_amount.text().replace("/=", ""))

                    except ValueError:
                        discountApplied.setText("0")
                        warning_box.setText("Values enter should be numbers!")
                        QTimer.singleShot(1500, warning_box.close)
                        warning_box.exec_()

                    finally:
                        mpesa_amount.setFlags(mpesa_amount.flags() ^ Qt.ItemIsEditable)

            finally:
                # Unblock signals after updates
                self.miniTable.blockSignals(False)

        self.miniTable.itemChanged.connect(update_cash_amount)

        # Set stretch last section to allow automatic adjustment
        self.miniTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.miniTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.miniTable.verticalHeader().setDefaultSectionSize(30)
        self.miniTable.setFixedHeight(213)

        self.miniTable.setMouseTracking(True)

        def cashPayment():
            # Temporarily block signals to avoid infinite loop
            mpesa_checkBox.blockSignals(True)
            mpesa_checkBox.setChecked(False)
            mpesa_checkBox.blockSignals(False)

            debt_checkBox.blockSignals(True)
            debt_checkBox.setChecked(False)
            debt_checkBox.blockSignals(False)

            discount_amount = self.miniTable.item(3, 1)
            cash_amount = self.miniTable.item(4, 1)
            mpesa_amount = self.miniTable.item(5, 1)

            if not self.switchMode:
                self.switchMode = True

            try:
                cash_amount.setFlags(cash_amount.flags() | Qt.ItemIsEditable)
                mpesa_amount.setFlags(mpesa_amount.flags() | Qt.ItemIsEditable)

                discount_amount.setText("0")
                cash_amount.setText(d)
                mpesa_amount.setText("0")

            finally:
                self.currentPayment = "cash"
                cash_amount.setFlags(cash_amount.flags() ^ Qt.ItemIsEditable)
                self.switchMode = False

        def mpesaPayment():
            self.currentPayment = "mpesa"
            # Temporarily block signals to avoid infinite loop
            cash_checkBox.blockSignals(True)
            cash_checkBox.setChecked(False)
            cash_checkBox.blockSignals(False)

            debt_checkBox.blockSignals(True)
            debt_checkBox.setChecked(False)
            debt_checkBox.blockSignals(False)

            discount_amount = self.miniTable.item(3, 1)
            cash_amount = self.miniTable.item(4, 1)
            mpesa_amount = self.miniTable.item(5, 1)

            if not self.switchMode:
                self.switchMode = True

            try:
                cash_amount.setFlags(cash_amount.flags() | Qt.ItemIsEditable)
                mpesa_amount.setFlags(mpesa_amount.flags() | Qt.ItemIsEditable)

                discount_amount.setText("0")
                cash_amount.setText("0")
                mpesa_amount.setText(d)

            finally:
                self.currentPayment = "mpesa"
                cash_amount.setFlags(cash_amount.flags() | Qt.ItemIsEditable)
                mpesa_amount.setFlags(mpesa_amount.flags() ^ Qt.ItemIsEditable)
                self.switchMode = False

        def debt_credit():
            cash_checkBox.blockSignals(True)
            cash_checkBox.setChecked(False)
            cash_checkBox.blockSignals(False)

            mpesa_checkBox.blockSignals(True)
            mpesa_checkBox.setChecked(False)
            mpesa_checkBox.blockSignals(False)

            discount_amount = self.miniTable.item(3, 1)
            cash_amount = self.miniTable.item(4, 1)
            mpesa_amount = self.miniTable.item(5, 1)

            if not self.switchMode:
                self.switchMode = True

            try:
                cash_amount.setFlags(cash_amount.flags() | Qt.ItemIsEditable)
                mpesa_amount.setFlags(mpesa_amount.flags() | Qt.ItemIsEditable)

                discount_amount.setText("0")
                cash_amount.setText("0")
                mpesa_amount.setText("0")

            finally:
                self.currentPayment = "debt"
                self.switchMode = False

        cash_checkBox = QCheckBox()
        cash_checkBox.setText("CASH")
        cash_checkBox.stateChanged.connect(cashPayment)

        mpesa_checkBox = QCheckBox()
        mpesa_checkBox.setText("MPESA")
        mpesa_checkBox.stateChanged.connect(mpesaPayment)

        debt_checkBox = QCheckBox()
        debt_checkBox.setText("Credit")
        debt_checkBox.stateChanged.connect(debt_credit)
        cash_checkBox.setChecked(True)

        checkBox_frameLayout.addWidget(cash_checkBox, alignment=Qt.AlignCenter)
        checkBox_frameLayout.addWidget(mpesa_checkBox, alignment=Qt.AlignCenter)
        checkBox_frameLayout.addWidget(debt_checkBox, alignment=Qt.AlignCenter)

        saveT_button = QPushButton()
        saveT_button.setText("SAVE")
        saveT_button.clicked.connect(self.save_sale)

        paymentFrame_layout.addWidget(checkBox_frame)
        paymentFrame_layout.addWidget(self.miniTable)
        paymentFrame_layout.addItem(QSpacerItem(0, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))
        paymentFrame_layout.addWidget(saveT_button, alignment=Qt.AlignRight)
        
    def save_sale(self):
        T_code = self.transaction_no.text()
        T_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            amount_payable = float(self.miniTable.item(0, 1).text().replace("/=", ""))
            item_count = float(self.miniTable.item(1, 1).text())
            discount_amount = float(self.miniTable.item(3, 1).text())
            cash_amount = float(self.miniTable.item(4, 1).text())
            mpesa_amount = float(self.miniTable.item(5, 1).text())
            amount_recv = cash_amount + mpesa_amount

            if self.currentPayment == 'cash':
                values = [T_code, T_date, item_count, amount_payable, cash_amount, mpesa_amount, discount_amount, "0",
                          amount_recv, "cash"]
                string_values = [str(element) for element in values]
                DbFunctions.database_insert(db_path=self.dbPath, into_selection="Transactions",
                                            new_values=tuple(string_values))

            elif self.currentPayment == 'mpesa':
                values = [T_code, T_date, item_count, amount_payable, cash_amount, mpesa_amount, discount_amount, "0",
                          amount_recv, "mpesa"]
                string_values = [str(element) for element in values]
                DbFunctions.database_insert(db_path=self.dbPath, into_selection="Transactions",
                                            new_values=tuple(string_values))

            elif self.currentPayment == 'debt':
                values = [T_code, T_date, item_count, amount_payable, cash_amount, mpesa_amount, discount_amount, "0",
                          amount_recv, "debt"]
                self.debt_dialog(data=values)

            self.save_data(T_code, T_date)

        except ValueError:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Wrong Data Format")
            msg_box.setText("Check if cash amount, mpesa amount or discount are numbers!")
            msg_box.setIcon(QMessageBox.Warning)
            QTimer.singleShot(3500, msg_box.close)
            msg_box.exec_()

    def save_data(self, T_code, T_date):
        if int(self.transaction_no.text()[8:]) + 1 <= 9999:
            new_code = self.transaction_no.text()[:8] + str(int(self.transaction_no.text()[8:]) + 1).zfill(4)
            self.transaction_no.setText(new_code)

        else:
            new_code = "HDC " + str(int(self.transaction_no.text()[4:7]) + 1).zfill(3) + '/0001'
            self.transaction_no.setText(new_code)

        for row in range(self.cart_widget.rowCount()):
            new_list = [T_code, T_date]
            row_values = [self.cart_widget.item(row, col).text() for col in range(self.cart_widget.columnCount())]
            new_list.append(row_values[3])
            new_list.append(row_values[5])
            new_list.append(row_values[4])
            new_list.append(row_values[6])
            DbFunctions.database_insert(db_path=self.dbPath, into_selection="Sales", new_values=tuple(new_list))

            product_id = row_values[1]  # Assuming column 1 in cart is the product_id

            if product_id not in self.non_quantifiable_items:
                stock_id = None
                for s_id, stock_info in self.stock_data.items():
                    for product in stock_info['products']:
                        if product['product_id'] == product_id:
                            stock_id = s_id
                            break
                    if stock_id is not None:
                        break

                # Check and deduct the quantity in stock_data
                current_stock_quantity = self.stock_data[stock_id]['quantity']
                new_stock_quantity = int(current_stock_quantity) - int(row_values[4])

                # Update the stock quantity in stock_data
                self.stock_data[stock_id]['quantity'] = new_stock_quantity

                # Reflect the update in the database
                DbFunctions.database_update(
                    db_path=self.dbPath,
                    what_selection="Stock",
                    set_selection="quantity",
                    new_value=new_stock_quantity,
                    where_selection="stock_id",
                    value_select=stock_id
                )

        self.cart_widget.clearContents()
        self.cart_widget.setRowCount(0)
        self.totalLabel.setText("0.00")
        self.saleWin.close()

    def debt_dialog(self, data):
        debtInfo = QDialog(self.saleWin)
        debtInfo.setFixedSize(QSize(300, 200))
        string_values = [str(element) for element in data]
        
        debtLayout = QVBoxLayout()
        debtInfo.setLayout(debtLayout)
        
        debtTable = QTableWidget()
        debtTable.setColumnCount(2)
        debtTable.verticalHeader().setVisible(False)
        debtTable.horizontalHeader().setStyleSheet(self.header_style)
        debtTable.horizontalHeader().setHighlightSections(False)
        debtTable.setStyleSheet(self.cell_style)
        debtTable.setAlternatingRowColors(True)
        debtTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        debtTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Description', 'Info']
        debtTable.setHorizontalHeaderLabels(column_headers)
        debtTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        debtTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        debtTable_base = {
            'Customer 1st Name *': "",
            'Customer 2nd Name *': "",
            'Customer Contact': "",
        }

        debtTable.setRowCount(len(debtTable_base))

        # Populate the table with dummy data
        editable_rows = [0, 1, 2]

        for row, (key, value) in enumerate(debtTable_base.items()):
            # Add the key as the first column
            key_item = QTableWidgetItem(str(key))
            key_item.setFlags(key_item.flags() ^ Qt.ItemIsEditable)
            debtTable.setItem(row, 0, key_item)

            # Insert the value in the next column (the last column in this case)
            item = QTableWidgetItem(str(value))

            # Check if this is the last column and if the row is editable
            if row in editable_rows:
                item.setFlags(item.flags() | Qt.ItemIsEditable)  # Allow editing
            else:
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # Disallow editing

            debtTable.setItem(row, 1, item)

        def save_debt_details():
            if debtTable.item(0, 1).text() and debtTable.item(1, 1).text():
                customer1 = debtTable.item(0, 1).text().capitalize()
                customer2 = debtTable.item(1, 1).text().capitalize()
                customer3 = debtTable.item(2, 1).text()

                amount_due = float(string_values[3]) - (float(string_values[4]) + float(string_values[5]) +
                                                        float(string_values[6]))

                debt_values = [string_values[0], string_values[1], string_values[2], customer1, customer2,
                               customer3,
                               string_values[3], string_values[4], string_values[5], string_values[6],
                               str(amount_due)]

                DbFunctions.database_insert(db_path=self.dbPath, into_selection="Credits",
                                            new_values=tuple(debt_values))
                DbFunctions.database_insert(db_path=self.dbPath, into_selection="Transactions",
                                            new_values=tuple(string_values))
                debtInfo.close()

            else:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Customer Information")
                msg_box.setText("Customer 1st Name and 2nd Name cannot be empty!")
                msg_box.setIcon(QMessageBox.Warning)
                QTimer.singleShot(3500, msg_box.close)
                msg_box.exec_()

        save_button = QPushButton()
        save_button.setText("SAVE")
        save_button.clicked.connect(save_debt_details)

        debtLayout.addWidget(debtTable)
        debtLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding))
        debtLayout.addWidget(save_button, alignment=Qt.AlignRight)

        debtInfo.exec_()
