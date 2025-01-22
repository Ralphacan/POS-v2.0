import DbFunctions
import sqlite3
from pandas import DataFrame, to_datetime
from time import strftime
from datetime import datetime, time
from reportlab.lib import colors
import plotly.graph_objects as go
import plotly.offline as pyo
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QDateTime, QDate
from PyQt5.QtWebEngineWidgets import QWebEngineView
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from PyQt5.QtWidgets import (QFrame, QLabel, QHBoxLayout, QLineEdit, QAction, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QVBoxLayout, QSpacerItem, QSizePolicy, QAbstractItemView, QDialog,
                             QPushButton, QFileDialog, QMessageBox, QDateEdit)


class ReportWindow:
    def __init__(self, Parent):
        self.todayStart = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        self.reportWin = QDialog(Parent)
        self.reportWin_layout = QVBoxLayout()

        self.header_style = """
                            QHeaderView::section {
                                background-color: #6c7ae0;
                                color: #fff;
                                padding: 2px;
                                font-size: 13x;
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

        self.selectionFrame = QFrame()
        self.plotArea_frame = QFrame()
        self.timeframe_combo = QComboBox()
        self.specifiedDay_calender = QDateEdit()
        self.rangeDay_start = QDateEdit()
        self.rangeDay_end = QDateEdit()
        self.custom_button = QPushButton("Load")
        self.currentPlot = None
        self.summaryTable = QTableWidget()
        self.salesChart = QWebEngineView()
        self.productsChart = QWebEngineView()

        self.window_setup()
        self.reportWin.exec_()

    def window_setup(self):
        self.reportWin.setFixedSize(QSize(950, 650))
        self.reportWin.setWindowTitle("Report Generation")
        self.reportWin_layout.setSpacing(0)
        self.reportWin_layout.setContentsMargins(15, 15, 15, 15)
        self.reportWin.setLayout(self.reportWin_layout)
        self.reportWin.setStyleSheet("background-color: #ACB9C4")

        self.table_header()
        self.chart_area()

        self.reportWin_layout.addWidget(self.selectionFrame, stretch=2)
        self.reportWin_layout.addWidget(self.plotArea_frame, stretch=20)

    def table_header(self):
        selectionLayout = QHBoxLayout()
        self.selectionFrame.setLayout(selectionLayout)
        selectionLayout.setSpacing(10)
        self.selectionFrame.setStyleSheet("background-color: #fff;"
                                          "border-bottom: 2px solid #888;"
                                          "border-top-left-radius: 5px;"
                                          "border-top-right-radius: 5px;")

        transact_heading = QLabel()
        transact_heading.setText("Reports")
        transact_heading.setStyleSheet("font-weight: bold;"
                                       "font-size: 15px;"
                                       "border-bottom: 0px solid #888;")

        periods = ["Today", "Yesterday", "Last 3 Days", "Last Week", "Last Month", "Last 3 Months", "Last 6 Months",
                   "Last 1 Year", "Specific Day", "Day Range"]
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

        full_button = QPushButton("Full Report")
        full_button.setStyleSheet("background-color: #2C55FB;"
                                    "color: #fff;"
                                    "border-radius: 5px;"
                                    "font-size: 13px;"
                                    "font-weight: bold;"
                                    "padding: 5px;"
                                    "border-bottom: 0px solid #888;")

        summary_button = QPushButton("Summary Report")
        summary_button.setStyleSheet("background-color: #2C55FB;"
                                    "color: #fff;"
                                    "border-radius: 5px;"
                                    "font-size: 13px;"
                                    "font-weight: bold;"
                                    "padding: 5px;"
                                    "border-bottom: 0px solid #888;")
        # export_button.clicked.connect(self.export_to_pdf)

        self.custom_button.setStyleSheet("background-color: green;"
                                    "color: #fff;"
                                    "border-radius: 5px;"
                                    "font-size: 13px;"
                                    "font-weight: bold;"
                                    "padding: 5px;"
                                    "border-bottom: 0px solid #888;")

        self.rangeDay_start.setVisible(False)
        self.rangeDay_end.setVisible(False)
        self.specifiedDay_calender.setVisible(False)
        self.custom_button.setVisible(False)

        selectionLayout.addWidget(transact_heading)
        selectionLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding))
        selectionLayout.addWidget(self.specifiedDay_calender)
        selectionLayout.addWidget(self.rangeDay_start)
        selectionLayout.addWidget(self.rangeDay_end)
        selectionLayout.addWidget(self.custom_button)
        selectionLayout.addWidget(self.timeframe_combo)
        selectionLayout.addWidget(full_button)
        selectionLayout.addWidget(summary_button)

    def chart_area(self):
        plotArea_frameLayout = QHBoxLayout()
        plotArea_frameLayout.setSpacing(0)
        plotArea_frameLayout.setContentsMargins(0, 0, 0, 0)
        self.plotArea_frame.setLayout(plotArea_frameLayout)

        charts_frame = QFrame()
        charts_frame_layout = QVBoxLayout()
        charts_frame_layout.setSpacing(2)
        charts_frame_layout.setContentsMargins(0, 0, 0, 0)
        charts_frame.setStyleSheet("background-color: red;"
                                    "border-bottom-left-radius: 5px;")
        charts_frame.setLayout(charts_frame_layout)
        charts_frame_layout.addWidget(self.salesChart)
        charts_frame_layout.addWidget(self.productsChart)

        self.summary_table_content()

        plotArea_frameLayout.addWidget(charts_frame, stretch=5)
        plotArea_frameLayout.addWidget(self.summaryTable, stretch=2)

    def summary_table_content(self):
        self.summaryTable.setColumnCount(2)
        self.summaryTable.verticalHeader().setVisible(False)
        self.summaryTable.horizontalHeader().setStyleSheet(self.header_style)
        self.summaryTable.horizontalHeader().setHighlightSections(False)
        self.summaryTable.setShowGrid(False)
        self.summaryTable.setStyleSheet(self.cell_style)
        self.summaryTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.summaryTable.setAlternatingRowColors(True)
        self.summaryTable.setFocusPolicy(Qt.NoFocus)

        column_headers = ['Description', 'Information']
        self.summaryTable.setHorizontalHeaderLabels(column_headers)

        # Set stretch last section to allow automatic adjustment
        self.summaryTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.summaryTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.summaryTable.verticalHeader().setDefaultSectionSize(40)

        self.summaryTable.setMouseTracking(True)

    def apply_filter(self):
        # Get current date and time
        current_datetime = QDateTime.currentDateTime()
        filter_type = self.timeframe_combo.currentText()

        # Define date range based on filter
        if filter_type == "Today":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)
            self.custom_button.setVisible(False)
            start_datetime = current_datetime.date().startOfDay()
            end_datetime = current_datetime.date().endOfDay()

            self.plot_data(dateType=filter_type, startDate=start_datetime, endDate=end_datetime)

        elif filter_type == "Yesterday":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)
            self.custom_button.setVisible(False)
            start_datetime = current_datetime.addDays(-1).date().startOfDay()
            end_datetime = current_datetime.addDays(-1).date().endOfDay()
            self.plot_data(dateType=filter_type, startDate=start_datetime, endDate=end_datetime)

        elif filter_type == "Last 3 Days":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)
            self.custom_button.setVisible(False)
            start_datetime = current_datetime.addDays(-2).date().startOfDay()
            end_datetime = current_datetime
            self.plot_data(dateType=filter_type, startDate=start_datetime, endDate=end_datetime)

        elif filter_type == "Last Week":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)
            self.custom_button.setVisible(False)
            start_datetime = current_datetime.addDays(-7).date().startOfDay()
            end_datetime = current_datetime
            self.plot_data(dateType=filter_type, startDate=start_datetime, endDate=end_datetime)

        elif filter_type == "Last Month":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)
            self.custom_button.setVisible(False)
            start_datetime = current_datetime.addMonths(-1).date().startOfDay()
            end_datetime = current_datetime
            self.plot_data(dateType=filter_type, startDate=start_datetime, endDate=end_datetime)

        elif filter_type == "Last 3 Months":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)
            self.custom_button.setVisible(False)
            start_datetime = current_datetime.addMonths(-3).date().startOfDay()
            end_datetime = current_datetime
            self.plot_data(dateType=filter_type, startDate=start_datetime, endDate=end_datetime)

        elif filter_type == "Last 6 Months":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)
            self.custom_button.setVisible(False)
            start_datetime = current_datetime.addMonths(-6).date().startOfDay()
            end_datetime = current_datetime
            self.plot_data(dateType=filter_type, startDate=start_datetime, endDate=end_datetime)

        elif filter_type == "Last 1 Year":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)
            self.custom_button.setVisible(False)
            start_datetime = current_datetime.addYears(-1).date().startOfDay()
            end_datetime = current_datetime
            self.plot_data(dateType=filter_type, startDate=start_datetime, endDate=end_datetime)

        elif filter_type == "Specific Day":
            self.rangeDay_start.setVisible(False)
            self.rangeDay_end.setVisible(False)

            self.specifiedDay_calender.setVisible(True)
            self.custom_button.setVisible(True)
            self.specifiedDay_calender.setCalendarPopup(True)

            current_date = QDate.currentDate()
            self.specifiedDay_calender.setMaximumDate(current_date)
            self.specifiedDay_calender.setDate(current_date)

            self.specifiedDay_calender.setStyleSheet("""
            QDateEdit {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
                background-color: #2E2E2E;
                color: white;
            }

            QDateEdit::down-arrow {
                background-color: #2E2E2E;
                color: white;
                image: url(assets/images/down.png);
                width: 24px;
                height: 24px;
            }
            
            QCalendarWidget QToolButton {
                background-color: white;
                color: #000;
                font-size: 12px;
                height: 30px;
                border-radius: 5px;
            }
        """)

            def load_data():
                current = self.specifiedDay_calender.text()
                date_obj = datetime.strptime(current, "%m/%d/%Y")
                startDatetime = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                endDatetime = datetime.combine(date_obj.date(),
                                               time(23, 59, 59)).strftime("%Y-%m-%d %H:%M:%S")

                self.plot_data(dateType=filter_type, startDate=startDatetime, endDate=endDatetime)

            self.custom_button.clicked.connect(load_data)

        elif filter_type == "Day Range":
            self.specifiedDay_calender.setVisible(False)
            self.rangeDay_start.setVisible(True)
            self.rangeDay_end.setVisible(True)

            self.custom_button.setVisible(True)
            self.rangeDay_start.setCalendarPopup(True)
            self.rangeDay_end.setCalendarPopup(True)

            current_date = QDate.currentDate()
            self.rangeDay_start.setMaximumDate(current_date)
            self.rangeDay_start.setDate(current_date)

            self.rangeDay_end.setMaximumDate(current_date)
            self.rangeDay_end.setDate(current_date)

            self.rangeDay_start.setStyleSheet("""
                QDateEdit {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #2E2E2E;
                    color: white;
                }

                QDateEdit::down-arrow {
                    background-color: #2E2E2E;
                    color: white;
                    image: url(assets/images/down.png);
                    width: 24px;
                    height: 24px;
                }

                QCalendarWidget QToolButton {
                    background-color: white;
                    color: #000;
                    font-size: 12px;
                    height: 30px;
                    border-radius: 5px;
                }
            """)
            self.rangeDay_end.setStyleSheet("""
                            QDateEdit {
                                border: 2px solid #4CAF50;
                                border-radius: 5px;
                                padding: 5px;
                                background-color: #2E2E2E;
                                color: white;
                            }

                            QDateEdit::down-arrow {
                                background-color: #2E2E2E;
                                color: white;
                                image: url(assets/images/down.png);
                                width: 24px;
                                height: 24px;
                            }

                            QCalendarWidget QToolButton {
                                background-color: white;
                                color: #000;
                                font-size: 12px;
                                height: 30px;
                                border-radius: 5px;
                            }
                        """)

            def load_data():
                userDate_1 = self.rangeDay_start.text()
                userDate_2 = self.rangeDay_start.text()

                date1_obj = datetime.strptime(userDate_1, "%m/%d/%Y").strftime("%Y-%m-%d %H:%M:%S")
                date2_obj = datetime.strptime(userDate_2, "%m/%d/%Y").strftime("%Y-%m-%d %H:%M:%S")

                if date1_obj > date2_obj:
                    self.plot_data(dateType=filter_type, startDate=date2_obj, endDate=date1_obj)

                else:
                    self.plot_data(dateType=filter_type, startDate=date1_obj, endDate=date2_obj)

            self.custom_button.clicked.connect(load_data)

    def plot_data(self, dateType, startDate, endDate):
        try:
            transaction_query = f"""SELECT * FROM Transactions WHERE strftime('%Y-%m-%d %H:%M:%S', transaction_date) >= ? 
            AND strftime('%Y-%m-%d %H:%M:%S', transaction_date) < ?"""

            sales_query = f"""SELECT * FROM Sales WHERE strftime('%Y-%m-%d %H:%M:%S', transaction_date) >= ? 
            AND strftime('%Y-%m-%d %H:%M:%S', transaction_date) < ?"""

            if isinstance(startDate, str):
                startDate = datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S")  # Adjust the format as needed
            else:
                startDate = startDate.toPyDateTime()

            if isinstance(endDate, str):
                endDate = datetime.strptime(endDate, "%Y-%m-%d %H:%M:%S")  # Adjust the format as needed
            else:
                endDate = endDate.toPyDateTime()

            conn = sqlite3.connect("assets/files/main.db")
            cursor = conn.cursor()
            cursor.execute(transaction_query, (startDate, endDate))
            collectedTransactions = cursor.fetchall()
            cursor.execute(sales_query, (startDate, endDate))
            collectedSales = cursor.fetchall()
            conn.close()

            sales_data = DataFrame(collectedSales, columns=['transaction_id', 'transaction_date', 'description',
                                                            'unit_price', 'quantity', 'total'])
            transaction_data = DataFrame(collectedTransactions, columns=['transaction_id', 'transaction_date',
                                                                         'item_count', 'total_cost', 'cash_amount',
                                                                         'mpesa_amount', 'discount', 'debt_amount',
                                                                         'amount_received', 'payment_mode'])

            # Convert transaction_date to datetime format
            sales_data['transaction_date'] = to_datetime(sales_data['transaction_date'], format='%Y-%m-%d %H:%M:%S')
            transaction_data['transaction_date'] = to_datetime(transaction_data['transaction_date'],
                                                               format='%Y-%m-%d %H:%M:%S')

            # Aggregate data based on the selected period
            if dateType in ["Today", "Yesterday", "Specific Day"]:
                sales_data['time_period'] = sales_data['transaction_date'].dt.hour
                transaction_data['time_period'] = transaction_data['transaction_date'].dt.hour

            elif dateType in ["Last 3 Days", "Last Week", "Last Month"]:
                sales_data['time_period'] = sales_data['transaction_date'].dt.date
                transaction_data['time_period'] = transaction_data['transaction_date'].dt.date

            else:
                sales_data['time_period'] = sales_data['transaction_date'].dt.to_period("W")
                transaction_data['time_period'] = transaction_data['transaction_date'].dt.to_period("W")

            # Group and sum totals
            groupedSales = sales_data.groupby('time_period')['total'].sum().reset_index()
            groupedSales['time_period'] = groupedSales['time_period'].astype(str)

            groupedTransact = transaction_data.groupby('time_period')['amount_received'].sum().reset_index()
            groupedTransact['time_period'] = groupedTransact['time_period'].astype(str)
            self.transaction_plot(groupedTransact)

        except Exception as e:
            print(e)


    def transaction_plot(self, data):
        fig = go.Figure(data=[go.Pie(
            labels=data.iloc[:, 0],
            values=data.iloc[:, 1],
            hole=0.4,  # Optional: Set this to > 0 for a donut chart
            textinfo='percent',  # Show labels and percentages
            marker=dict(colors=['#209DFF', '#FFA500', '#66CC99', '#FF3333'])  # Custom colors
        )])

        # Customize the layout
        fig.update_layout(
            title={
                'text': "Sales Distribution",
                'x': 0.5,  # Center the title
                'xanchor': 'center',
                'yanchor': 'top'
            },
            paper_bgcolor='rgb(19, 23, 34)',
            plot_bgcolor='rgb(19, 23, 34)',
            margin=dict(l=0, r=0, t=0, b=0)
        )

        # Generate HTML for Plotly figure
        html = '<html><body style="background-color: #131722;">'
        html += pyo.plot(fig, output_type='div', include_plotlyjs='cdn', config={'displayModeBar': False,
                                                                                 'scrollZoom': False})
        html += ' </body></html>'
        self.productsChart.setHtml(html)

        if len(data) <= 7:
            fig = go.Figure(data=[go.Bar(
                x=data.iloc[:, 0],  # First column for x-axis
                y=data.iloc[:, 1],  # Second column for y-axis
                marker=dict(
                    color='rgba(77, 169, 240, 0.7)',  # Bar color
                    line=dict(color="#209DFF", width=1)  # Outline color and thickness
                )
            )])

            fig.layout.xaxis.fixedrange = True
            fig.layout.yaxis.fixedrange = True

            fig.update_layout(
                hoverlabel=dict(
                    bgcolor="rgba(255, 255, 255, 0.8)",  # Background color (e.g., light white)
                    font_size=12,  # Font size
                    font_color="black"  # Font color
                ),

                paper_bgcolor='rgb(19, 23, 34)',  # Background color
                plot_bgcolor='rgb(19, 23, 34)',  # Plot area background color

                title={
                    'text': "Sales",  # Title text
                    'y': 0.9,  # Vertical alignment of the title
                    'x': 0.5,  # Centered horizontally
                    'xanchor': 'center',
                    'yanchor': 'top',
                },

                xaxis=dict(
                    rangeslider=dict(visible=False),
                    zeroline=False,
                    showgrid=False,
                    gridwidth=0.5,
                    gridcolor='#383E4D',
                    color='white'  # White color for x-axis labels
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=0.5,
                    gridcolor='#383E4D',
                    title_standoff=10,
                    color='white'  # White color for y-axis labels
                ),
                margin=dict(l=2, r=0, t=0, b=0),  # Remove margins
                hovermode='x unified'
            )

            # Generate HTML for Plotly figure
            html = '<html><body style="background-color: #131722;">'
            html += pyo.plot(fig, output_type='div', include_plotlyjs='cdn', config={'displayModeBar': False,
                                                                                     'scrollZoom': False})
            html += ' </body></html>'
            self.salesChart.setHtml(html)

        else:
            fig = go.Figure(data=[go.Scatter(
                x=data.iloc[:, 0],
                y=data.iloc[:, 1],
                mode='lines',  # Line mode for the chart
                fill='tozeroy',  # Filling the area below the line
                fillcolor='rgba(77, 169, 240, 0.1)',  # Light blue area color
                line=dict(color="#209DFF", width=2)  # Line color and thickness
            )])

            fig.layout.xaxis.fixedrange = True
            fig.layout.yaxis.fixedrange = True

            fig.update_layout(
                hoverlabel=dict(
                    bgcolor="rgba(255, 255, 255, 0.8)",  # Background color (e.g., light white)
                    font_size=12,  # Font size
                    font_color="black"  # Font color
                ),

                paper_bgcolor='rgb(19, 23, 34)',
                plot_bgcolor='rgb(19, 23, 34)',

                title={
                    'text': "Sales",  # Title text
                    'y': 0.9,  # Vertical alignment of the title
                    'x': 0.5,  # Centered horizontally
                    'xanchor': 'center',
                    'yanchor': 'top',
                },

                xaxis=dict(
                    rangeslider=dict(visible=False),
                    zeroline=False,
                    showgrid=False,
                    gridwidth=0.5,
                    gridcolor='#383E4D',
                    color='white'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=0.5,
                    gridcolor='#383E4D',
                    title_standoff=10,
                    color='white'  # White color for y-axis labels
                ),
                margin=dict(l=2, r=0, t=0, b=0),  # Remove margins
                hovermode='x unified'
            )

            # Generate HTML for Plotly figure
            html = '<html><body style="background-color: #131722;">'
            html += pyo.plot(fig, output_type='div', include_plotlyjs='cdn', config={'displayModeBar': False,
                                                                                     'scrollZoom': False})
            html += ' </body></html>'
            self.salesChart.setHtml(html)

