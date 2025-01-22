import DbFunctions
from time import strftime
from datetime import datetime
from reportlab.lib import colors
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QDateTime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from PyQt5.QtWidgets import (QFrame, QLabel, QHBoxLayout, QLineEdit, QAction, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QVBoxLayout, QSpacerItem, QSizePolicy, QAbstractItemView, QDialog,
                             QPushButton, QFileDialog, QMessageBox)


class TransactionWindow:
    def __init__(self, Parent):
        self.todayStart = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        self.transactionWin = QDialog(Parent)
        self.transactionWin_layout = QVBoxLayout()

        self.selectionFrame = QFrame()
        self.transactionTable = QTableWidget()
        self.timeframe_combo = QComboBox()

        self.transactions = DbFunctions.database_all_lookup(db_path="assets/files/main.db", what_selection="*",
                                                       from_selection="Transactions")
        self.window_setup()
        self.transactionWin.exec_()

    def window_setup(self):
        self.transactionWin.setFixedSize(QSize(900, 600))
        self.transactionWin.setWindowTitle("Transaction History")
        self.transactionWin_layout.setSpacing(0)
        self.transactionWin_layout.setContentsMargins(15, 15, 15, 15)
        self.transactionWin.setLayout(self.transactionWin_layout)
        self.transactionWin.setStyleSheet("background-color: #ACB9C4")
        
        self.table_header()
        self.table_content()
        
        self.transactionWin_layout.addWidget(self.selectionFrame, stretch=2)
        self.transactionWin_layout.addWidget(self.transactionTable, stretch=20)

    def table_header(self):
        selectionLayout = QHBoxLayout()
        self.selectionFrame.setLayout(selectionLayout)
        selectionLayout.setSpacing(10)
        self.selectionFrame.setStyleSheet("background-color: #fff;"
                                          "border-bottom: 2px solid #888;"
                                          "border-top-left-radius: 5px;"
                                          "border-top-right-radius: 5px;")
        
        transact_heading = QLabel()
        transact_heading.setText("Transaction History")
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


        periods = ["All Transactions", "Today", "Yesterday", "Last 3 Days", "Last Week", "Last Month", "Last 3 Months",
                   "Last 6 Months", "Last 1 Year"]
        self.timeframe_combo.addItems(periods)
        self.timeframe_combo.setEditable(False)
        self.timeframe_combo.setStyleSheet('''QComboBox {
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
        self.timeframe_combo.currentTextChanged.connect(self.apply_filter)

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
        selectionLayout.addWidget(self.timeframe_combo)
        selectionLayout.addWidget(export_button)

    def table_content(self):
        self.transactionTable.setColumnCount(10)
        self.transactionTable.verticalHeader().setVisible(False)
        self.transactionTable.horizontalHeader().setStyleSheet("""
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
        self.transactionTable.horizontalHeader().setHighlightSections(False)
        self.transactionTable.setShowGrid(False)
        self.transactionTable.setStyleSheet("""
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
        self.transactionTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transactionTable.setAlternatingRowColors(True)
        self.transactionTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Transaction ID', 'Transaction Date', 'Item Count', 'Total', 'Cash Amount', 'Mpesa Amount',
                          'Discount', 'Debt Amount', 'Received', 'Mode']
        self.transactionTable.setHorizontalHeaderLabels(column_headers)

        # Set stretch last section to allow automatic adjustment
        self.transactionTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.transactionTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.transactionTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.transactionTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.transactionTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.transactionTable.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.transactionTable.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.transactionTable.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.transactionTable.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.transactionTable.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.transactionTable.verticalHeader().setDefaultSectionSize(40)

        self.transactionTable.setMouseTracking(True)

        self.transactionTable.setRowCount(len(self.transactions))  # Set row count to match the data

        # Populate the table with data
        for row_position, row_data in enumerate(self.transactions):
            for col, item in enumerate(row_data):
                cell_item = QTableWidgetItem(str(item))
                self.transactionTable.setItem(row_position, col, cell_item)
                cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)

    def search_table(self, searchWidget):
        """Filter table rows based on search input."""
        search_text = searchWidget.text().lower()

        # Loop through table rows and hide those that do not match the search
        for row_ in range(self.transactionTable.rowCount()):
            match = False
            for col_ in range(self.transactionTable.columnCount()):
                item_ = self.transactionTable.item(row_, col_)
                if item_ and search_text in item_.text().lower():
                    match = True
                    break  # If one item in the row matches, no need to check other columns
            self.transactionTable.setRowHidden(row_, not match)

    def apply_filter(self):
        # Get current date and time
        current_datetime = QDateTime.currentDateTime()

        # Determine the selected filter type
        filter_type = self.timeframe_combo.currentText()

        # Define date range based on filter
        if filter_type == "Today":
            start_datetime = current_datetime.date().startOfDay()
            end_datetime = current_datetime.date().endOfDay()
        elif filter_type == "Yesterday":
            start_datetime = current_datetime.addDays(-1).date().startOfDay()
            end_datetime = current_datetime.addDays(-1).date().endOfDay()
        elif filter_type == "Last 3 Days":
            start_datetime = current_datetime.addDays(-2).date().startOfDay()
            end_datetime = current_datetime
        elif filter_type == "Last Week":
            start_datetime = current_datetime.addDays(-7).date().startOfDay()
            end_datetime = current_datetime
        elif filter_type == "Last Month":
            start_datetime = current_datetime.addMonths(-1).date().startOfDay()
            end_datetime = current_datetime
        elif filter_type == "Last 3 Months":
            start_datetime = current_datetime.addMonths(-3).date().startOfDay()
            end_datetime = current_datetime
        elif filter_type == "Last 6 Months":
            start_datetime = current_datetime.addMonths(-6).date().startOfDay()
            end_datetime = current_datetime
        elif filter_type == "Last 1 Year":
            start_datetime = current_datetime.addYears(-1).date().startOfDay()
            end_datetime = current_datetime
        else:
            # Show all if "All" is selected
            for row in range(self.transactionTable.rowCount()):
                self.transactionTable.setRowHidden(row, False)
            return

        # Filter rows based on the date range
        for row in range(self.transactionTable.rowCount()):
            # Get the date from the table
            date_item = self.transactionTable.item(row, 1)  # Assuming date is in the 3rd column
            if date_item is None:
                continue

            # Parse the date and time from the table item
            row_datetime = QDateTime.fromString(date_item.text(), "yyyy-MM-dd hh:mm:ss")

            # Hide or show the row based on the datetime range
            if start_datetime <= row_datetime <= end_datetime:
                self.transactionTable.setRowHidden(row, False)
            else:
                self.transactionTable.setRowHidden(row, True)

    def export_to_pdf(self):
        # File path for PDF
        pdf_file_path = QFileDialog.getExistingDirectory(self.transactionWin, "Select where to save the file?")

        # Create a SimpleDocTemplate object
        if pdf_file_path:
            pdf_file_path +=  "/Transactions-" + strftime('%d-%B-%Y-%H-%M-%S-%p') + ".pdf"

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
            heading = Paragraph("Transaction History Report", heading_style)
            subheading = Paragraph("List of transactions with details for the period:\n"
                                   f"{self.timeframe_combo.currentText()}", subheading_style)

            # Initialize data list with headers
            data = [['Transaction ID', 'Transaction Date', 'Item Count', 'Total', 'Cash Amount', 'Mpesa Amount',
                     'Discount', 'Debt Amount', 'Received', 'Mode']]

            # Collect visible rows data
            for row in range(self.transactionTable.rowCount()):
                if not self.transactionTable.isRowHidden(row):  # Only include visible rows
                    row_data = []
                    for col in range(self.transactionTable.columnCount()):
                        item = self.transactionTable.item(row, col)
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
                f"Transaction History for the period {self.timeframe_combo.currentText()} has been saved to:\n"
                f"{pdf_file_path}")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
