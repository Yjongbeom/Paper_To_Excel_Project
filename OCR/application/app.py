import sys
import subprocess
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from gui import OCRApp
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv()

openai_key = os.getenv("OPENAI_KEY")
upstage_key = os.getenv("UPSTAGE_KEY")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    icon_path = os.path.join(os.path.dirname(__file__), "Icon", "Logo.png").replace("\\", "/")
    
    app.setWindowIcon(QIcon(icon_path))
    
    window = OCRApp()
    window.show()
    sys.exit(app.exec_())