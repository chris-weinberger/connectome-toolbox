# This is the main GUI file that will be used to create the GUI for the data analysis app.
# The GUI will allow users to upload a CSV file, specify columns to aggregate into a region of interest (RSA), and compute RSA on connections to/from specified regions.
# The results will be displayed in a text area, and a plot will be shown in a separate window.
from qtpy.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QDialog, QHBoxLayout
)
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
from analysis import build_corr_matrix  # Assuming this is your analysis function

class DataAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Analysis App")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.uploaded_data = None
        self.upload_button = QPushButton("Upload CSV File")
        self.upload_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.upload_button)

        self.column_input = QLineEdit(self)
        self.column_input.setPlaceholderText("Enter column name(s) separated by commas to aggregate into RSA region")
        self.layout.addWidget(self.column_input)

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

            preview_df = df.head(5)
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
            (to_matrix, from_matrix) = build_corr_matrix(self.uploaded_data, columns, filter_flag=True, min_num_connections=3)
            self.show_plot(to_matrix, from_matrix)

        except Exception as e:
            self.result_text.setText(f"Error: {str(e)}")

    def show_plot(self, to_matrix, from_matrix):
        plot_window_to_plot = PlotWindow(self, display_data=to_matrix)

        plot_window_from_plot = PlotWindow(self, display_data=from_matrix)

        # TO DO: Pass the data to the plot window for display -- test this
        plot_window_to_plot.show(title = "To Matrix")
        plot_window_from_plot.show(title = "From Matrix")

class PlotWindow(QDialog):
    def __init__(self, parent=None, display_data=None):
        super().__init__(parent)
        self.setWindowTitle("Analysis Plot")
        self.setGeometry(200, 200, 600, 400)

        self.layout = QHBoxLayout(self)

        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        self.data = display_data

        ax = self.figure.add_subplot(111)
        #  Important: Replace this example plot with your actual data from analyze_data
        try:
            # Assuming analyze_data returns a matplotlib figure or data suitable for plotting
            if isinstance(results, plt.Figure): # If analyze_data already returns a figure
                self.figure = results # Use the returned figure
                self.canvas = FigureCanvas(self.figure) # Update the canvas
                ax = self.figure.axes[0] if self.figure.axes else self.figure.add_subplot(111) # Get or create axes

            elif isinstance(results, tuple) and len(results) == 2:  # If it returns (x, y) data
                x, y = results
                ax.plot(x, y)
                ax.set_title("Analysis Plot")
            elif isinstance(results, pd.DataFrame): # If it returns a dataframe
                results.plot(ax=ax)
                ax.set_title("Analysis Plot")

            else:  # Handle other potential return types and create a default plot if needed
                ax.plot([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])  # Example plot
                ax.set_title("Sample Plot")

        except Exception as e:
            ax.plot([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])  # Example plot
            ax.set_title(f"Error Plotting: {e}")

        self.layout.addWidget(self.canvas)
        self.canvas.draw()

    def show_plot(self, title="Analysis Plot"):
        plt.figure(figsize=(20, 20))
        sns.heatmap(self.data, fmt=".2f", cbar=True, square=True, xticklabels=True, yticklabels=True)
        plt.title(title)
        plt.tight_layout()
        plt.show()