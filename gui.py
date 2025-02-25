# This is the main GUI file that will be used to create the GUI for the data analysis app.
# The GUI will allow users to upload a CSV file, specify columns to aggregate into a region of interest (RSA), and compute RSA on connections to/from specified regions.
# The results will be displayed in a text area, and a plot will be shown in a separate window.
from qtpy.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QDialog, QComboBox
)
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar

import seaborn as sns
from analysis import build_corr_matrix  # Assuming this is your analysis function

class DataAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anatomical Representational Similarity of Neural Data")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.uploaded_data = None
        self.upload_button = QPushButton("Upload CSV File")
        self.upload_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.upload_button)

        self.column_input = QLineEdit(self)
        self.column_input.setPlaceholderText("Enter column name(s) separated by commas to aggregate into RSA region")
        self.layout.addWidget(self.column_input)

        # Dropdown (QComboBox)
        self.distance_metric = "pearson"  # Default value
        self.metric_dropdown = QComboBox()
        self.metric_dropdown.addItems(["pearson", "spearman", "cosine", "braycurtis"])  # Add your options
        # Connect to a function when the selection is changed
        self.metric_dropdown.currentIndexChanged.connect(self.metric_dropdown_selection_changed)
        self.layout.addWidget(self.metric_dropdown)


        self.analyze_button = QPushButton("Compute RSA on connections to/from specified regions")
        self.analyze_button.clicked.connect(self.run_analysis)
        self.layout.addWidget(self.analyze_button)

        # Table Widget for Data Preview (Initially Hidden)
        self.table_widget = QTableWidget()
        self.table_widget.setMinimumHeight(200)
        self.table_widget.setVisible(False)  # Hide initially
        self.layout.addWidget(self.table_widget)

        # Text Area for Results
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        self.setLayout(self.layout)
        self.file_path = ""

    def metric_dropdown_selection_changed(self, index):
        selected_option = self.metric_dropdown.itemText(index)
        print(f"Selected option: {selected_option}")  # Or do something else with the selection
        # You can use the selected_option to change the plot or other aspects of your application
        self.distance_metric = selected_option

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)")
        if file_path:
            self.file_path = file_path
            self.result_text.setText(f"Loaded file: {file_path}")
            self.preview_data(file_path)

    def preview_data(self, file_path):
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path, index_col=0)  # Use first column as index
            elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                df = pd.read_excel(file_path, index_col=0)  # Use first column as index
            else:
                self.result_text.setText("Unsupported file format.")
                return
            
            self.uploaded_data = df

            preview_df = df.head(10)
            self.display_table(preview_df)
            self.table_widget.setVisible(True)

        except Exception as e:
            self.result_text.setText(f"Error loading file: {str(e)}")

    def display_table(self, df):
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns)
        self.table_widget.setVerticalHeaderLabels(df.index.astype(str))

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
            (to_matrix, from_matrix) = build_corr_matrix(self.uploaded_data, columns, filter_flag=True, min_num_connections=3, distance_metric=self.distance_metric)
            self.show_plot(to_matrix, from_matrix)

        except Exception as e:
            self.result_text.setText(f"Error: {str(e)}")

    def show_plot(self, to_matrix, from_matrix):
        self.plot_window_to_plot = PlotWindow(self, display_data=to_matrix, window_title="To Matrix")
        self.plot_window_from_plot = PlotWindow(self, display_data=from_matrix, window_title="From Matrix")

        self.plot_window_to_plot.show()
        self.plot_window_from_plot.show()

class PlotWindow(QDialog):
    def __init__(self, parent=None, display_data=None, window_title="Analysis Plot"):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout(self)

        self.figure = plt.Figure(figsize=(4, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        # Add the Matplotlib toolbar for navigation (zoom, pan, save)
        self.toolbar = NavigationToolbar(self.canvas, self)  # Pass self for parent

        self.data = display_data

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.canvas.draw()

        self.plot_data()  # Call plotting function

    def plot_data(self):

        ax = self.figure.add_subplot(111)  # Create a subplot
        sns.heatmap(self.data, fmt=".2f", cbar=True, square=True, xticklabels=True, yticklabels=True, ax=ax)
        ax.set_title("Representational Similarity Analysis in Connectivity Patterns")

        self.canvas.draw()