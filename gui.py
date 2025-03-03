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
from analysis import build_corr_matrix, build_corr_matrix_full, compute_mds  # Assuming this is your analysis function

class DataAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anatomical Representational Similarity of Neural Data")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.uploaded_data = None
        self.upload_button = QPushButton("Upload CSV File")
        self.upload_button.clicked.connect(self.load_data)
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

        # Add button to run RSA analysis
        self.analyze_button = QPushButton("Compute RSA on connections to/from specified regions")
        self.analyze_button.clicked.connect(self.run_rsa)
        self.layout.addWidget(self.analyze_button)
        self.rsa_data = None

        # Add a button to run MDS analysis
        self.mds_button = QPushButton("Run MDS Analysis")
        self.mds_button.clicked.connect(self.run_mds)
        self.layout.addWidget(self.mds_button)
        self.mds_button.setVisible(False)  # Initially hidden

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


    # IN DEVELOPMENT
    def load_data(self, matrix_csv_path, region_names=None):
        """
        Imports a CSV file into a pandas DataFrame and numbers the rows and columns.

        Args:
            matrix_csv_path (str): Path to the CSV file containing the matrix data.

        Returns:
            pandas.DataFrame: A pandas DataFrame containing the matrix data with numbered rows and columns.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)")
        if file_path:
            self.file_path = file_path
            self.result_text.setText(f"Loaded file: {file_path}")
            self.preview_data(file_path)
        df = pd.read_csv(matrix_csv_path)  # Read without header

        if region_names is not None:
            # process region names for index and column
            df.index = region_names
            df.columns = region_names
        else:
            df.index = range(1, len(df) + 1)  # Number the rows
            df.columns = range(1, len(df.columns) + 1)  # Number the columns

        self.result_text.setText(f"Loaded matrix data from: {df.index}")
        self.uploaded_data = df

        preview_df = df.head(10)
        self.display_table(preview_df)
        self.table_widget.setVisible(True)


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

    def run_rsa(self):
        if not self.file_path:
            self.result_text.setText("Please upload a file first.")
            return
        try:
            if self.column_input.text() == "":
                self.rsa_data = build_corr_matrix_full(self.uploaded_data, distance_metric=self.distance_metric)
                self.show_plot(viz_type='RSA')
            else:
                # Split the input text by commas and remove any leading/trailing whitespace
                columns = self.column_input.text().split(",")
                columns = [col.strip() for col in columns]
                
                # define RSA matrices for incoming and outgoing connections
                self.rsa_data = build_corr_matrix(self.uploaded_data, columns, filter_flag=True, min_num_connections=3, distance_metric=self.distance_metric)
                self.show_plot(viz_type='RSA')
                
                self.mds_button.setVisible(True) # Show the MDS button

        except Exception as e:
            self.result_text.setText(f"Error: {str(e)}")

    def run_mds(self):
        self.result_text.setText("Running MDS analysis...")
        to_matrix = self.rsa_data[0]
        from_matrix = self.rsa_data[1]
        self.result_text.setText("got the matrices extracted")
        try:
            mds_result_to = compute_mds(to_matrix)
            mds_result_from = compute_mds(from_matrix)
            self.show_plot(mds_result_to, mds_result_from, 'MDS')

        except Exception as e:
            self.result_text.setText(f"Error: {str(e)}")

    def show_plot(self, viz_type='RSA'):
        try:
            # if they haven't entered any columns, just run RSA on the full matrix and display that
            if (self.column_input.text() == ""):
                rsa_data = self.rsa_data
                self.plot_window_rsa = PlotWindow(self, display_data=rsa_data, viz_type=viz_type)
                self.plot_window_rsa.show()
            else:
                # get to_matrix and from_matrix from the tuple
                to_matrix = self.rsa_data[0]
                from_matrix = self.rsa_data[1]

                self.plot_window_to_plot = PlotWindow(self, display_data=to_matrix, viz_type=viz_type, window_title="To Matrix")
                self.plot_window_from_plot = PlotWindow(self, display_data=from_matrix, viz_type=viz_type, window_title="From Matrix")

                self.plot_window_to_plot.show()
                self.plot_window_from_plot.show()
        except Exception as e:
            self.result_text.setText(f"Error: {str(e)}")

class PlotWindow(QDialog):
    def __init__(self, parent=None, display_data=None, viz_type='RSA', window_title="Analysis Plot"):
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

        if viz_type == 'RSA':
            self.plot_rsa_data()
        elif viz_type == 'MDS':
            self.plot_mds_data()
        else:
            raise ValueError("Invalid visualization type")

    def plot_rsa_data(self):

        ax = self.figure.add_subplot(111)  # Create a subplot
        sns.heatmap(self.data, fmt=".2f", cbar=True, square=True, xticklabels=True, yticklabels=True, ax=ax)
        ax.set_title("Representational Dissimilarity in Connectivity Patterns")

        self.canvas.draw()

    def plot_mds_data(self):
        ax = self.figure.add_subplot(111)  # Create a subplot
        sns.scatterplot(
            x='Dim1', y='Dim2', 
            data=self.data, 
            ax=ax,
            s=100,
            marker='o',
            color='red'
        )

        ax.set_title("Representational Dissimilarity in Connectivity Patterns")
        for label, (x, y) in self.data.iterrows():
            ax.text(x, y, label, fontsize=12, ha='right', va='center')