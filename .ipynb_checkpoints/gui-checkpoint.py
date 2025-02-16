from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QLineEdit, QTextEdit, 
    QTableWidget, QTableWidgetItem, QScrollArea
)
import pandas as pd
from analysis import analyze_data

class DataAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connectome RSA Toolbox")
        self.setGeometry(100, 100, 600, 400)  # Increased size for better display

        self.layout = QVBoxLayout()

        self.upload_button = QPushButton("Upload csv File")
        self.upload_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.upload_button)

        self.column_input = QLineEdit(self)
        self.column_input.setPlaceholderText("Enter column name(s) separated by commas")
        self.layout.addWidget(self.column_input)

        self.analyze_button = QPushButton("Analyze Data")
        self.analyze_button.clicked.connect(self.run_analysis)
        self.layout.addWidget(self.analyze_button)

        # Scrollable Table for Data Preview
        self.table_widget = QTableWidget()
        self.table_widget.setMinimumHeight(150)  # Set a fixed height
        self.layout.addWidget(self.table_widget)

        # Scrollable Text Area for Results
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        self.setLayout(self.layout)
        self.file_path = ""

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)")
        if file_path:
            self.file_path = file_path
            self.result_text.setText(f"Loaded file: {file_path}")
            self.preview_data(file_path)

    def preview_data(self, file_path):
        """Loads the first 5 rows of the dataset and displays them in a table."""
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path, header=0, index_col=0)
            elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                df = pd.read_excel(file_path, header=0, index_col=0)
            else:
                self.result_text.setText("Unsupported file format.")
                return

            # Limit to first 5 rows
            preview_df = df.head(5)
            self.display_table(preview_df)

        except Exception as e:
            self.result_text.setText(f"Error loading file: {str(e)}")

    def display_table(self, df):
        """Displays a Pandas DataFrame in the QTableWidget."""
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))

        self.table_widget.resizeColumnsToContents()

    def run_analysis(self):
        if not self.file_path:
            self.result_text.setText("Please upload a file first.")
            return
        
        columns = self.column_input.text().split(",")
        columns = [col.strip() for col in columns]

        try:
            results = analyze_data(self.file_path, columns)
            self.result_text.setText(results)
        except Exception as e:
            self.result_text.setText(f"Error: {str(e)}")
