import DbFunctions
from time import strftime
from reportlab.lib import colors
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from PyQt5.QtWidgets import (QFrame, QLabel, QHBoxLayout, QLineEdit, QAction, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QVBoxLayout, QSpacerItem, QSizePolicy, QAbstractItemView, QDialog,
                             QPushButton, QMenu, QMessageBox, QFileDialog)

class CreditWindow:
    def __init__(self, Parent):
        self.debtWin = QDialog(Parent)
        self.debtWin_layout = QVBoxLayout()

        self.selectionFrame = QFrame()
        self.debtTable = QTableWidget()
        self.choice_combo = QComboBox()

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

        self.creditData = DbFunctions.database_all_lookup(db_path="assets/files/main.db", what_selection="*",
                                                            from_selection="Credits")

        self.window_setup()
        self.debtWin.exec_()
        
    def window_setup(self):
        self.debtWin.setFixedSize(QSize(950, 600))
        self.debtWin.setWindowTitle("Credits and Debts Window")
        self.debtWin_layout.setSpacing(0)
        self.debtWin_layout.setContentsMargins(15, 15, 15, 15)
        self.debtWin.setLayout(self.debtWin_layout)
        self.debtWin.setStyleSheet("background-color: #ACB9C4")

        self.table_header()
        self.table_content()

        self.debtWin_layout.addWidget(self.selectionFrame, stretch=2)
        self.debtWin_layout.addWidget(self.debtTable, stretch=20)

    def table_header(self):
        selectionLayout = QHBoxLayout()
        self.selectionFrame.setLayout(selectionLayout)
        selectionLayout.setSpacing(10)
        self.selectionFrame.setStyleSheet("background-color: #fff;"
                                          "border-bottom: 2px solid #888;"
                                          "border-top-left-radius: 5px;"
                                          "border-top-right-radius: 5px;")

        transact_heading = QLabel()
        transact_heading.setText("Credit History")
        transact_heading.setStyleSheet("font-weight: bold;"
                                       "font-size: 15px;"
                                       "border-bottom: 0px solid #888;")

        search_input = QLineEdit()
        search_input.setStyleSheet("""
                           QLineEdit {
                               border: 1px solid gray;
                               border-bottom: 2px solid blue;
                               padding-left: 8px;
                               background-color: #F5F7FA;
                               color: #333;
                               font-size: 16px;
                               border-radius: 5px;
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
        search_input.addAction(QAction(QIcon(icon_pixmap), "", search_input), QLineEdit.LeadingPosition)
        search_input.setPlaceholderText("Search any field")
        search_input.setMaximumWidth(450)
        search_input.textChanged.connect(lambda: self.search_table(search_input))

        export_button = QPushButton("Export")
        export_button.setStyleSheet("background-color: #2C55FB;"
                                    "color: #fff;"
                                    "border-radius: 5px;"
                                    "font-size: 13px;"
                                    "font-weight: bold;"
                                    "padding: 5px;"
                                    "border-bottom: 0px solid #888;")
        export_button.clicked.connect(self.export_to_pdf)

        selectionLayout.addWidget(transact_heading)
        selectionLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding))
        selectionLayout.addWidget(search_input)
        selectionLayout.addWidget(export_button)

    def table_content(self):
        self.debtTable.setColumnCount(11)
        self.debtTable.verticalHeader().setVisible(False)
        self.debtTable.horizontalHeader().setStyleSheet("""
        QHeaderView::section {
                    background-color: #fff;
                    color: #000;
                    padding: 5px;
                    font-size: 12px;
                    border-width: 0px 0px 2px 0px;
                    border-style: solid;
                    border-bottom: 2px solid #888;
                }

        """)
        self.debtTable.horizontalHeader().setHighlightSections(False)
        self.debtTable.setShowGrid(False)
        self.debtTable.setStyleSheet("""
        QTableWidget {
            background-color: #fff;
            border: 0px solid #fff;
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 5px;
        }  

        QTableWidget::item {
            padding: 0px 0px 0px 15px;
            border-width: 0px 0px 1px 0px;
            border-style: solid;
            border-color: #888;
        }

        QTableWidget::item:Selected {
            color: #000;
            background-color: lightblue;
        }     
        """)
        self.debtTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.debtTable.setAlternatingRowColors(True)
        self.debtTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Transaction ID', 'Date', 'Item Count', 'First Name', 'Second Name', 'Contact',
                          'Total', 'Cash Deposit', 'Mpesa Deposit', 'Discount', 'Amount Due']
        self.debtTable.setHorizontalHeaderLabels(column_headers)

        # Set stretch last section to allow automatic adjustment
        self.debtTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.debtTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.debtTable.horizontalHeader().setSectionResizeMode(10, QHeaderView.ResizeToContents)
        self.debtTable.verticalHeader().setDefaultSectionSize(40)

        self.debtTable.setMouseTracking(True)

        self.debtTable.setRowCount(len(self.creditData))  # Set row count to match the data

        # Populate the table with data
        for row_position, row_data in enumerate(self.creditData):
            for col, item in enumerate(row_data):
                cell_item = QTableWidgetItem(str(item))
                self.debtTable.setItem(row_position, col, cell_item)
                cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)

        def show_context_menu(pos):
            # Get the index of the item that was clicked
            index = self.debtTable.indexAt(pos)

            if index.isValid():
                row = index.row()
                row_ = []

                for _col in range(self.debtTable.columnCount()):
                    _item = self.debtTable.item(row, _col)
                    row_.append(_item.text() if _item else "")

                # Create and show the context menu
                context_menu = QMenu(self.debtTable)
                context_menu.setStyleSheet("""
                    QMenu {  /* Hover effect */
                        background-color: #fff;
                        color: #000;
                    }

                    QMenu::item:selected {
                        background-color: #0078D7;
                        color: white;
                    }
                """)

                edit_action = QAction(QIcon('assets/images/partial.png'), "Partial Credit Payment", self.debtTable)
                edit_action.triggered.connect(lambda: self.partial_pay(data=row_))
                context_menu.addAction(edit_action)

                remove_action = QAction(QIcon('assets/images/full.png'), "Full Credit Payment", self.debtTable)
                remove_action.triggered.connect(lambda: self.full_pay(data=row_))
                context_menu.addAction(remove_action)

                context_menu.exec_(self.debtTable.viewport().mapToGlobal(pos))

        self.debtTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.debtTable.customContextMenuRequested.connect(show_context_menu)

    def search_table(self, searchWidget):
        """Filter table rows based on search input."""
        search_text = searchWidget.text().lower()

        # Loop through table rows and hide those that do not match the search
        for row_ in range(self.debtTable.rowCount()):
            match = False
            for col_ in range(self.debtTable.columnCount()):
                item_ = self.debtTable.item(row_, col_)
                if item_ and search_text in item_.text().lower():
                    match = True
                    break  # If one item in the row matches, no need to check other columns
            self.debtTable.setRowHidden(row_, not match)

    def export_to_pdf(self):
        # File path for PDF
        pdf_file_path = QFileDialog.getExistingDirectory(self.debtWin, "Select where to save the file?")

        # Create a SimpleDocTemplate object
        if pdf_file_path:
            pdf_file_path +=  "/Credits-" + strftime('%d-%B-%Y-%H-%M-%S-%p') + ".pdf"

            top_margin = 20  # e.g., 20 units
            bottom_margin = 20
            left_margin = 20
            right_margin = 20

            # Create a SimpleDocTemplate object with landscape orientation and custom margins
            pdf = SimpleDocTemplate(
                pdf_file_path,
                pagesize=landscape(A4),
                topMargin=top_margin,
                bottomMargin=bottom_margin,
                leftMargin=left_margin,
                rightMargin=right_margin
            )

            styles = getSampleStyleSheet()
            heading_style = styles['Title']
            subheading_style = styles['Heading3']

            # Create the heading and subheading paragraphs
            company = Paragraph("Hudumia Cyber", heading_style)
            heading = Paragraph("Credit History Report", heading_style)
            subheading = Paragraph("List of credit transactions offered to customers", subheading_style)

            # Initialize data list with headers
            data = [['Transaction ID', 'Date', 'Item Count', 'First Name', 'Second Name', 'Contact', 'Total',
                     'Cash Deposit', 'Mpesa Deposit', 'Discount', 'Amount Due']]

            # Collect visible rows data
            for row in range(self.debtTable.rowCount()):
                if not self.debtTable.isRowHidden(row):  # Only include visible rows
                    row_data = []
                    for col in range(self.debtTable.columnCount()):
                        item = self.debtTable.item(row, col)
                        row_data.append(item.text() if item is not None else "")
                    data.append(row_data)

            # Create a Table with the data
            table = Table(data)

            # Add a style to the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.forestgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            # Build the PDF with the table
            elements = [company, Spacer(1, 5), heading, Spacer(1, 12), subheading,
                        Spacer(1, 24), table]

            # Build the PDF
            pdf.build(elements)

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("File Saved")
            msg_box.setText(
                f"Credit History has been saved to:\n"
                f"{pdf_file_path}")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

    def partial_pay(self, data):
        debtInfo = QDialog(self.debtWin)
        debtInfo.setFixedSize(QSize(300, 200))
        debtInfo.setWindowTitle("Partial Debt Payment")

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
        debtTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        debtTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        debtTable_base = {
            'Amount due': str(data[10]) + " /=",
            'Cash Deposit': "0",
            'Mpesa Deposit': "0",
            'Discount': "0",
        }

        debtTable.setRowCount(len(debtTable_base))

        # Populate the table with dummy data
        editable_rows = [1, 2, 3]

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
            try:
                cash = float(debtTable.item(1, 1).text())
                mpesa = float(debtTable.item(2, 1).text())
                discount = float(debtTable.item(3, 1).text())

                if float(data[10]) - discount > (cash + mpesa):
                    if (debtTable.item(0, 1).text() or debtTable.item(1, 1).text() or
                            debtTable.item(2, 1).text()):

                        new_cash = float(data[7]) + cash
                        new_mpesa = float(data[8]) + mpesa
                        new_discount = float(data[9]) + discount
                        new_amount_due = (float(data[10]) - discount) - (cash + mpesa)

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions", set_selection="cash_amount",
                            new_value=new_cash, where_selection="transaction_code", value_select=data[0]
                        )
                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions", set_selection="mpesa_amount",
                            new_value=new_mpesa, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions", set_selection="discount",
                            new_value=new_discount, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions", set_selection="amount_received",
                            new_value=new_cash + new_mpesa, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Credits", set_selection="cash_deposit",
                            new_value=new_cash, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Credits", set_selection="mpesa_deposit",
                            new_value=new_mpesa, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Credits", set_selection="discount",
                            new_value=new_discount, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Credits", set_selection="amount_due",
                            new_value=new_amount_due, where_selection="transaction_code", value_select=data[0]
                        )

                        debtInfo.close()

                    else:
                        msg_box = QMessageBox()
                        msg_box.setWindowTitle("Credit Information")
                        msg_box.setText("For Partial pay specify an amount to update!")
                        msg_box.setIcon(QMessageBox.Warning)
                        QTimer.singleShot(3500, msg_box.close)
                        msg_box.exec_()

                else:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Credit Information")
                    msg_box.setText("Amount entered is detected as full pay!")
                    msg_box.setIcon(QMessageBox.Warning)
                    QTimer.singleShot(3500, msg_box.close)
                    msg_box.exec_()

            except ValueError:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Credit Information")
                msg_box.setText("Any amount update should be a number!")
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

    def full_pay(self, data):
        debtInfo = QDialog(self.debtWin)
        debtInfo.setFixedSize(QSize(300, 200))
        debtInfo.setWindowTitle("Full Debt Payment")

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
        debtTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        debtTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        debtTable_base = {
            'Amount due': str(data[10]) + " /=",
            'Cash Deposit': "0",
            'Mpesa Deposit': "0",
            'Discount': "0",
        }

        debtTable.setRowCount(len(debtTable_base))

        # Populate the table with dummy data
        editable_rows = [1, 2, 3]

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
            try:
                cash = float(debtTable.item(1, 1).text())
                mpesa = float(debtTable.item(2, 1).text())
                discount = float(debtTable.item(3, 1).text())

                if (float(data[10]) - discount) - (cash + mpesa) == 0:
                    if (debtTable.item(0, 1).text() or debtTable.item(1, 1).text() or
                            debtTable.item(2, 1).text()):

                        new_cash = float(data[7]) + cash
                        new_mpesa = float(data[8]) + mpesa
                        new_discount = float(data[9]) + discount

                        if max(new_cash, new_mpesa) == new_cash:
                            mode = "cash"

                        else:
                            mode = "mpesa"

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions", set_selection="cash_amount",
                            new_value=new_cash, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions", set_selection="mpesa_amount",
                            new_value=new_mpesa, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions", set_selection="discount",
                            new_value=new_discount, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions", set_selection="amount_received",
                            new_value=new_cash + new_mpesa, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_update(
                            db_path="assets/files/main.db", what_selection="Transactions",
                            set_selection="payment_mode",
                            new_value=mode, where_selection="transaction_code", value_select=data[0]
                        )

                        DbFunctions.database_delete(db_path="assets/files/main.db", from_selection="Credits",
                                                    where_selection="transaction_code", value_select=data[0])

                        debtInfo.close()

                    else:
                        msg_box = QMessageBox()
                        msg_box.setWindowTitle("Credit Information")
                        msg_box.setText("For Full pay specify an amount to update!")
                        msg_box.setIcon(QMessageBox.Warning)
                        QTimer.singleShot(3500, msg_box.close)
                        msg_box.exec_()

                else:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Credit Information")
                    msg_box.setText("Amount entered is detected as partial pay!")
                    msg_box.setIcon(QMessageBox.Warning)
                    QTimer.singleShot(3500, msg_box.close)
                    msg_box.exec_()

            except ValueError:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Credit Information")
                msg_box.setText("Any amount update should be a number!")
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