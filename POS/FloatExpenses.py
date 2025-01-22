import DbFunctions
from time import strftime
from datetime import datetime
from reportlab.lib import colors
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from PyQt5.QtWidgets import (QFrame, QLabel, QHBoxLayout, QLineEdit, QAction, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QVBoxLayout, QSpacerItem, QSizePolicy, QAbstractItemView, QDialog,
                             QPushButton, QFileDialog, QMessageBox)


class FloatWindow:
    def __init__(self, Parent):
        self.floatWin = QDialog(Parent)
        self.floatWin_layout = QVBoxLayout()

        self.selectionFrame = QFrame()
        self.floatTable = QTableWidget()

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

        self.floatData = DbFunctions.database_all_lookup(db_path="assets/files/main.db", what_selection="*",
                                                       from_selection="Float_Expenses")
        self.window_setup()
        self.floatWin.exec_()

    def window_setup(self):
        self.floatWin.setFixedSize(QSize(550, 600))
        self.floatWin.setWindowTitle("Float and Expenses")
        self.floatWin_layout.setSpacing(0)
        self.floatWin_layout.setContentsMargins(15, 15, 15, 15)
        self.floatWin.setLayout(self.floatWin_layout)
        self.floatWin.setStyleSheet("background-color: #ACB9C4")
        
        self.table_header()
        self.float_display()

        self.floatWin_layout.addWidget(self.selectionFrame, stretch=2)
        self.floatWin_layout.addWidget(self.floatTable, stretch=20)
        
    def table_header(self):
        selectionLayout = QHBoxLayout()
        self.selectionFrame.setLayout(selectionLayout)
        selectionLayout.setSpacing(10)
        self.selectionFrame.setStyleSheet("background-color: #fff;"
                                          "border-bottom: 2px solid #888;"
                                          "border-top-left-radius: 5px;"
                                          "border-top-right-radius: 5px;")

        transact_heading = QLabel()
        transact_heading.setText("Float & Expenses")
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

        add_button = QPushButton("Add Expense")
        add_button.setStyleSheet("background-color: red;"
                                    "color: #fff;"
                                    "border-radius: 5px;"
                                    "font-size: 13px;"
                                    "font-weight: bold;"
                                    "padding: 5px;"
                                    "border-bottom: 0px solid #888;")
        add_button.clicked.connect(self.add_expense)

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
        selectionLayout.addWidget(add_button)
        selectionLayout.addWidget(export_button)

    def float_display(self):
        self.floatTable.setColumnCount(4)
        self.floatTable.verticalHeader().setVisible(False)
        self.floatTable.horizontalHeader().setStyleSheet("""
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
        self.floatTable.horizontalHeader().setHighlightSections(False)
        self.floatTable.setShowGrid(False)
        self.floatTable.setStyleSheet("""
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
        self.floatTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.floatTable.setAlternatingRowColors(True)
        self.floatTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Date', 'Type', 'Amount', 'Reason']
        self.floatTable.setHorizontalHeaderLabels(column_headers)

        # Set stretch last section to allow automatic adjustment
        self.floatTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.floatTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.floatTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.floatTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.floatTable.verticalHeader().setDefaultSectionSize(40)

        self.floatTable.setMouseTracking(True)

        self.floatTable.setRowCount(len(self.floatData))  # Set row count to match the data

        # Populate the table with data
        for row_position, row_data in enumerate(self.floatData):
            for col, item in enumerate(row_data):
                cell_item = QTableWidgetItem(str(item))
                self.floatTable.setItem(row_position, col, cell_item)
                cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)
        
    def search_table(self, searchWidget):
        """Filter table rows based on search input."""
        search_text = searchWidget.text().lower()

        # Loop through table rows and hide those that do not match the search
        for row_ in range(self.floatTable.rowCount()):
            match = False
            for col_ in range(self.floatTable.columnCount()):
                item_ = self.floatTable.item(row_, col_)
                if item_ and search_text in item_.text().lower():
                    match = True
                    break  # If one item in the row matches, no need to check other columns
            self.floatTable.setRowHidden(row_, not match)

    def add_expense(self):
        floatInfo = QDialog(self.floatWin)
        floatInfo.setFixedSize(QSize(250, 145))
        floatInfo.setWindowTitle("Expense log")

        floatLayout = QVBoxLayout()
        floatInfo.setLayout(floatLayout)

        floatTable = QTableWidget()
        floatTable.setColumnCount(2)
        floatTable.verticalHeader().setVisible(False)
        floatTable.horizontalHeader().setStyleSheet(self.header_style)
        floatTable.horizontalHeader().setHighlightSections(False)
        floatTable.setStyleSheet(self.cell_style)
        floatTable.setAlternatingRowColors(True)
        floatTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        floatTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Description', 'Info']
        floatTable.setHorizontalHeaderLabels(column_headers)
        floatTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        floatTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        floatTable_base = {
            'Amount': "",
            'Reason': ""
        }

        floatTable.setRowCount(len(floatTable_base))

        # Populate the table with dummy data
        editable_rows = [0, 1]

        for row, (key, value) in enumerate(floatTable_base.items()):
            # Add the key as the first column
            key_item = QTableWidgetItem(str(key))
            key_item.setFlags(key_item.flags() ^ Qt.ItemIsEditable)
            floatTable.setItem(row, 0, key_item)

            # Insert the value in the next column (the last column in this case)
            item = QTableWidgetItem(str(value))

            # Check if this is the last column and if the row is editable
            if row in editable_rows:
                item.setFlags(item.flags() | Qt.ItemIsEditable)  # Allow editing
            else:
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # Disallow editing

            floatTable.setItem(row, 1, item)

        def save_float_details():
            try:
                amount = float(floatTable.item(0, 1).text().strip())
                reason = floatTable.item(1, 1).text().strip()

                if amount > 0 and len(reason) > 3:
                    new_list = [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Expense", amount, reason]
                    DbFunctions.database_insert(db_path="assets/files/main.db", into_selection="Float_Expenses",
                                                new_values=tuple(new_list))
                    floatInfo.close()

                else:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Expenses")
                    msg_box.setText("Check that the amount is greater than 0\nThere must be a reason!")
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.exec_()

            except ValueError:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Expenses")
                msg_box.setText("Any amount update should be a number!")
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.exec_()

        save_button = QPushButton()
        save_button.setText("SAVE")
        save_button.clicked.connect(save_float_details)

        floatLayout.addWidget(floatTable)
        floatLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding))
        floatLayout.addWidget(save_button, alignment=Qt.AlignRight)

        floatInfo.exec_()

    def export_to_pdf(self):
        # File path for PDF
        pdf_file_path = QFileDialog.getExistingDirectory(self.floatWin, "Select where to save the file?")

        # Create a SimpleDocTemplate object
        if pdf_file_path:
            pdf_file_path +=  "/Float&Expenses-" + strftime('%d-%B-%Y-%H-%M-%S-%p') + ".pdf"

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
            heading = Paragraph("Float and Expenses Report", heading_style)
            subheading = Paragraph("List of Float & Expenses with details", subheading_style)

            # Initialize data list with headers
            data = [['Date', 'Type', 'Amount', 'Reason']]

            # Collect visible rows data
            for row in range(self.floatTable.rowCount()):
                if not self.floatTable.isRowHidden(row):  # Only include visible rows
                    row_data = []
                    for col in range(self.floatTable.columnCount()):
                        item = self.floatTable.item(row, col)
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
                f"Float & Expenses History has been saved to:\n"f"{pdf_file_path}")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()