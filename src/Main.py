import sys
import os
import time
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import Qt, QIcon, QPixmap

from ui.main_window import CharacterConverter


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Character Converter Toolbox")

    splash_path = resource_path("assets/cct-splash.png")
    if os.path.exists(splash_path):
        screen_splash = QPixmap(splash_path)
        intro_screen = QSplashScreen(screen_splash)
        intro_screen.show()
        app.processEvents()

        for i in range(1, 6):
            intro_screen.showMessage(
                f"{i*20}% loading", Qt.AlignBottom | Qt.AlignCenter, Qt.black
            )
            app.processEvents()
            time.sleep(0.6)
    else:
        intro_screen = QSplashScreen()
        intro_screen.show()
        app.processEvents()
        for i in range(1, 6):
            intro_screen.showMessage(
                f"{i*20}% loading", Qt.AlignBottom | Qt.AlignCenter, Qt.white
            )
            app.processEvents()
            time.sleep(0.6)

    icon_path = resource_path("assets/icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = CharacterConverter()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
