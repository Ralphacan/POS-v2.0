import DbFunctions
from time import strftime
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from PyQt5.QtWidgets import (QFrame, QLabel, QHBoxLayout, QLineEdit, QAction, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QVBoxLayout, QSpacerItem, QSizePolicy, QAbstractItemView, QDialog,
                             QPushButton, QMenu, QInputDialog, QMessageBox, QFileDialog)

class StockWindow:
    def __init__(self, Parent):
        self.todayStart = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        self.stockWin = QDialog(Parent)
        self.stockWin_layout = QVBoxLayout()

        self.selectionFrame = QFrame()
        self.tableFrame = QFrame()
        self.inventoryTable = QTableWidget()
        self.logsTable = QTableWidget()
        self.choice_combo = QComboBox()

        self.stocks = DbFunctions.database_all_lookup(db_path="assets/files/main.db", what_selection="*",
                                                            from_selection="Stock")

        self.logs = DbFunctions.database_all_lookup(db_path="assets/files/main.db", what_selection="*",
                                                      from_selection="stock_change")
        self.window_setup()
        self.stockWin.exec_()

    def window_setup(self):
        self.stockWin.setFixedSize(QSize(700, 600))
        self.stockWin.setWindowTitle("Stock Management")
        self.stockWin_layout.setSpacing(0)
        self.stockWin_layout.setContentsMargins(15, 15, 15, 15)
        self.stockWin.setLayout(self.stockWin_layout)
        self.stockWin.setStyleSheet("background-color: #ACB9C4")

        self.table_header()
        tableFrame_layout = QVBoxLayout()
        tableFrame_layout.setSpacing(0)
        tableFrame_layout.setContentsMargins(0, 0, 0, 0)
        self.tableFrame.setLayout(tableFrame_layout)
        tableFrame_layout.addWidget(self.inventoryTable)
        tableFrame_layout.addWidget(self.logsTable)
        self.logsTable.setVisible(False)
        self.stock_inventory()

        self.stockWin_layout.addWidget(self.selectionFrame, stretch=2)
        self.stockWin_layout.addWidget(self.tableFrame, stretch=20)

    def table_header(self):
        selectionLayout = QHBoxLayout()
        self.selectionFrame.setLayout(selectionLayout)
        selectionLayout.setSpacing(10)
        self.selectionFrame.setStyleSheet("background-color: #fff;"
                                          "border-bottom: 2px solid #888;"
                                          "border-top-left-radius: 5px;"
                                          "border-top-right-radius: 5px;")

        transact_heading = QLabel()
        transact_heading.setText("Stock Management Panel")
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

        periods = ["Stock Inventory", "Stock Log"]
        self.choice_combo.addItems(periods)
        self.choice_combo.setEditable(False)
        self.choice_combo.setStyleSheet('''QComboBox {
                        color: #454C57;
                        background-color: #E7E7E8;  /* Set background color */
                        border: 0px solid #555;  /* Set border color */
                        padding: 5px;            /* Add some padding */
                        font: 13px;
                        border-radius: 5px;
                    }

                    QComboBox QAbstractItemView {
                        background-color: #fff;  /* Set drop-down item background color */
                        color: #000;             /* Set drop-down item text color */
                        selection-background-color: #1317225;  /* Set selected item background color */
                        selection-color: #fff;   /* Set selected item text color */
                    }

                    QComboBox::drop-down {
                        border-left: 0px solid #007BFF;
                        width: 25px;
                        background-color: #E7E7E8;
                        border-radius: 5px;
                    }

                    QComboBox::down-arrow {
                        image: url(assets/images/down.png); /* Path to custom down arrow icon */
                        width: 14px;
                        height: 14px;
                    }
                    ''')
        self.choice_combo.currentTextChanged.connect(self.apply_filter)

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
        selectionLayout.addWidget(self.choice_combo)
        selectionLayout.addWidget(export_button)

    def stock_inventory(self):
        self.inventoryTable.setColumnCount(4)
        self.inventoryTable.verticalHeader().setVisible(False)
        self.inventoryTable.horizontalHeader().setStyleSheet("""
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
        self.inventoryTable.horizontalHeader().setHighlightSections(False)
        self.inventoryTable.setShowGrid(False)
        self.inventoryTable.setStyleSheet("""
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
        self.inventoryTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.inventoryTable.setAlternatingRowColors(True)
        self.inventoryTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Stock ID', 'Stock Name', 'Quantity', 'last updated']
        self.inventoryTable.setHorizontalHeaderLabels(column_headers)

        # Set stretch last section to allow automatic adjustment
        self.inventoryTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.inventoryTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.inventoryTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.inventoryTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.inventoryTable.verticalHeader().setDefaultSectionSize(40)

        self.inventoryTable.setMouseTracking(True)

        self.inventoryTable.setRowCount(len(self.stocks))  # Set row count to match the data

        # Populate the table with data
        for row_position, row_data in enumerate(self.stocks):
            for col, item in enumerate(row_data):
                cell_item = QTableWidgetItem(str(item))
                self.inventoryTable.setItem(row_position, col, cell_item)
                cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)

        def stock_addition(data):
            quantity, ok = QInputDialog.getInt(self.stockWin, "Enter Quantity", "Quantity to add:", 1, 1, 1000, 1)

            if ok:
                currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                stockLog = [data[0], data[1], currentTime, data[2], str(int(data[2]) + quantity), "addition"]
                stockLog_values = [str(element) for element in stockLog]
                DbFunctions.database_insert(db_path="assets/files/main.db", into_selection="stock_change",
                                            new_values=tuple(stockLog_values))

                DbFunctions.database_update(
                    db_path="assets/files/main.db",
                    what_selection="Stock",
                    set_selection="quantity",
                    new_value=str(int(data[2]) + quantity),
                    where_selection="stock_id",
                    value_select=str(data[0])
                )

                DbFunctions.database_update(
                    db_path="assets/files/main.db",
                    what_selection="Stock",
                    set_selection="last_updated",
                    new_value=currentTime,
                    where_selection="stock_id",
                    value_select=str(data[0])
                )

                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("Stock Update")
                msg_box.setText("Stock addition was successful!")
                QTimer.singleShot(1500, msg_box.close)
                msg_box.exec_()

        def stock_waste(data):
            quantity, ok = QInputDialog.getInt(self.stockWin, "Enter Quantity", "Waste Amount:", 1, 1, int(data[2]), 1)

            if ok:
                currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                stockLog = [data[0], data[1], currentTime, data[2], str(int(data[2]) - quantity), "waste"]
                stockLog_values = [str(element) for element in stockLog]
                DbFunctions.database_insert(db_path="assets/files/main.db", into_selection="stock_change",
                                            new_values=tuple(stockLog_values))

                DbFunctions.database_update(
                    db_path="assets/files/main.db",
                    what_selection="Stock",
                    set_selection="quantity",
                    new_value=str(int(data[2]) - quantity),
                    where_selection="stock_id",
                    value_select=str(data[0])
                )

                DbFunctions.database_update(
                    db_path="assets/files/main.db",
                    what_selection="Stock",
                    set_selection="last_updated",
                    new_value=currentTime,
                    where_selection="stock_id",
                    value_select=str(data[0])
                )

                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("Stock Update")
                msg_box.setText("Stock waste logging was successful!")
                QTimer.singleShot(2500, msg_box.close)
                msg_box.exec_()

        def show_context_menu(pos):
            # Get the index of the item that was clicked
            index = self.inventoryTable.indexAt(pos)

            if index.isValid():
                row = index.row()
                row_ = []

                for _col in range(self.inventoryTable.columnCount()):
                    _item = self.inventoryTable.item(row, _col)
                    row_.append(_item.text() if _item else "")

                # Create and show the context menu
                context_menu = QMenu(self.inventoryTable)
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

                edit_action = QAction(QIcon('assets/images/warehouse.png'), "Add More Stock", self.inventoryTable)
                edit_action.triggered.connect(lambda: stock_addition(data=row_))
                context_menu.addAction(edit_action)

                remove_action = QAction(QIcon('assets/images/remove-st.png'), "Waste", self.inventoryTable)
                remove_action.triggered.connect(lambda: stock_waste(data=row_))
                context_menu.addAction(remove_action)

                context_menu.exec_(self.inventoryTable.viewport().mapToGlobal(pos))

        self.inventoryTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.inventoryTable.customContextMenuRequested.connect(show_context_menu)

    def stock_log(self):
        self.logsTable.setColumnCount(6)
        self.logsTable.verticalHeader().setVisible(False)
        self.logsTable.horizontalHeader().setStyleSheet("""
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
        self.logsTable.horizontalHeader().setHighlightSections(False)
        self.logsTable.setShowGrid(False)
        self.logsTable.setStyleSheet("""
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
        self.logsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.logsTable.setAlternatingRowColors(True)
        self.logsTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Stock ID', 'Stock Name', 'Change Date', 'Prev Qty', 'New Qty', 'Reason']
        self.logsTable.setHorizontalHeaderLabels(column_headers)

        # Set stretch last section to allow automatic adjustment
        self.logsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.logsTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.logsTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.logsTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.logsTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.logsTable.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.logsTable.verticalHeader().setDefaultSectionSize(40)

        self.logsTable.setMouseTracking(True)

        self.logsTable.setRowCount(len(self.logs))  # Set row count to match the data

        # Populate the table with data
        for row_position, row_data in enumerate(self.logs):
            for col, item in enumerate(row_data):
                cell_item = QTableWidgetItem(str(item))
                self.logsTable.setItem(row_position, col, cell_item)
                cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)

    def search_table(self, searchWidget):
        """Filter table rows based on search input."""
        search_text = searchWidget.text().lower()

        if self.choice_combo.currentText() == "Stock Inventory":
            # Loop through table rows and hide those that do not match the search
            for row_ in range(self.inventoryTable.rowCount()):
                match = False
                for col_ in range(self.inventoryTable.columnCount()):
                    item_ = self.inventoryTable.item(row_, col_)
                    if item_ and search_text in item_.text().lower():
                        match = True
                        break  # If one item in the row matches, no need to check other columns
                self.inventoryTable.setRowHidden(row_, not match)

        elif self.choice_combo.currentText() == "Stock Log":
            # Loop through table rows and hide those that do not match the search
            for row_ in range(self.logsTable.rowCount()):
                match = False
                for col_ in range(self.logsTable.columnCount()):
                    item_ = self.logsTable.item(row_, col_)
                    if item_ and search_text in item_.text().lower():
                        match = True
                        break  # If one item in the row matches, no need to check other columns
                self.logsTable.setRowHidden(row_, not match)

    def apply_filter(self):
        # Determine the selected filter type
        filter_type = self.choice_combo.currentText()

        if self.inventoryTable.isVisible() and filter_type == "Stock Log":
            self.inventoryTable.setVisible(False)
            self.logsTable.setVisible(True)

            self.stock_log()

        elif self.logsTable.isVisible() and filter_type == "Stock Inventory":
            self.logsTable.setVisible(False)
            self.inventoryTable.setVisible(True)

            self.stock_inventory()

    def export_to_pdf(self):
        # File path for PDF
        pdf_file_path = QFileDialog.getExistingDirectory(self.stockWin, "Select where to save the file?")

        # Create a SimpleDocTemplate object
        if pdf_file_path:
            pdf_file_path +=  "/StockReport-" + strftime('%d-%B-%Y-%H-%M-%S-%p') + ".pdf"

            top_margin = 20  # e.g., 20 units
            bottom_margin = 20
            left_margin = 20
            right_margin = 20

            # Create a SimpleDocTemplate object with landscape orientation and custom margins
            pdf = SimpleDocTemplate(
                pdf_file_path,
                pagesize=A4,
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
            heading = Paragraph("Stock Management Report", heading_style)

            if self.choice_combo.currentText() == "Stock Inventory":
                subheading = Paragraph("Quantity of Items in Stock", subheading_style)

                # Initialize data list with headers
                data = [['Stock ID', 'Stock Description', 'Quantity', 'Last Updated']]

                # Collect visible rows data
                for row in range(self.inventoryTable.rowCount()):
                    if not self.inventoryTable.isRowHidden(row):  # Only include visible rows
                        row_data = []
                        for col in range(self.inventoryTable.columnCount()):
                            item = self.inventoryTable.item(row, col)
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

            else:
                subheading = Paragraph("Stock Update Logs", subheading_style)

                # Initialize data list with headers
                data = [['Stock ID', 'Stock Description', 'Change Date', 'Prev Qty', 'New Qty', 'Reason']]

                # Collect visible rows data
                for row in range(self.logsTable.rowCount()):
                    if not self.logsTable.isRowHidden(row):  # Only include visible rows
                        row_data = []
                        for col in range(self.logsTable.columnCount()):
                            item = self.logsTable.item(row, col)
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
                f"Stock Report has been saved to:\n{pdf_file_path}")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()