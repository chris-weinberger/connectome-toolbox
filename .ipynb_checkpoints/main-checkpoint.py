from PyQt6.QtWidgets import QApplication
from gui import DataAnalysisApp
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataAnalysisApp()
    window.show()
    sys.exit(app.exec())
    