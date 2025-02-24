import sys
import seaborn as sns
import pandas as pd
import numpy as np

from qtpy import QtWidgets  # Use qtpy for QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class MainWindow(QtWidgets.QMainWindow):  # Inherit from qtpy's QMainWindow
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seaborn + QtPy Test")

        # Create a central widget
        self.central_widget = QtWidgets.QWidget()  # Use qtpy's QWidget
        self.setCentralWidget(self.central_widget)

        # Create layout
        layout = QtWidgets.QVBoxLayout()  # Use qtpy's QVBoxLayout
        self.central_widget.setLayout(layout)

        # Generate test data
        df = pd.DataFrame(np.random.rand(10, 2), columns=["X", "Y"])

        # Create Matplotlib figure
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x="X", y="Y", ax=ax)

        # Embed figure in Qt
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        self.show()

# Run Application
app = QtWidgets.QApplication(sys.argv)  # Use qtpy's QApplication
window = MainWindow()
sys.exit(app.exec())