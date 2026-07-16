from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor


def apply_theme(window):
    app = QApplication.instance()
    app.setStyle("Fusion")

    dark_palette = QPalette()

    dark_bg = QColor(30, 30, 35)
    darker_bg = QColor(20, 20, 25)
    widget_bg = QColor(40, 40, 45)
    highlight = QColor(76, 175, 80)
    highlight_hover = QColor(56, 155, 60)
    text_color = QColor(220, 220, 220)
    text_disabled = QColor(100, 100, 100)
    border_color = QColor(50, 50, 55)

    dark_palette.setColor(QPalette.ColorRole.Window, dark_bg)
    dark_palette.setColor(QPalette.ColorRole.WindowText, text_color)
    dark_palette.setColor(QPalette.ColorRole.Base, darker_bg)
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, widget_bg)
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(40, 40, 45))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
    dark_palette.setColor(QPalette.ColorRole.Text, text_color)
    dark_palette.setColor(QPalette.ColorRole.Button, widget_bg)
    dark_palette.setColor(QPalette.ColorRole.ButtonText, text_color)
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 100, 100))
    dark_palette.setColor(QPalette.ColorRole.Link, highlight)
    dark_palette.setColor(QPalette.ColorRole.Highlight, highlight)
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.PlaceholderText, text_disabled)

    app.setPalette(dark_palette)

    window.setStyleSheet(f"""
        QMainWindow {{
            background-color: {dark_bg.name()};
        }}
        
        QGroupBox {{
            border: 1px solid {border_color.name()};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 10px;
            font-weight: bold;
            background-color: {widget_bg.name()};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: {highlight.name()};
        }}
        
        QPushButton {{
            background-color: {highlight.name()};
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
            color: white;
            min-width: 100px;
        }}
        
        QPushButton:hover {{
            background-color: {highlight_hover.name()};
        }}
        
        QPushButton:pressed {{
            background-color: {darker_bg.name()};
        }}
        
        QPushButton:disabled {{
            background-color: {text_disabled.name()};
            color: {darker_bg.name()};
        }}
        
        QLabel {{
            color: {text_color.name()};
        }}
        
        QProgressBar {{
            border: 1px solid {border_color.name()};
            border-radius: 4px;
            text-align: center;
            background-color: {darker_bg.name()};
            color: {text_color.name()};
        }}
        
        QProgressBar::chunk {{
            background-color: {highlight.name()};
            border-radius: 3px;
        }}
        
        QListWidget {{
            background-color: {darker_bg.name()};
            border: 1px solid {border_color.name()};
            border-radius: 4px;
            padding: 4px;
            color: {text_color.name()};
            outline: none;
        }}
        
        QListWidget::item {{
            padding: 4px;
            border-bottom: 1px solid {border_color.name()};
        }}
        
        QListWidget::item:selected {{
            background-color: {highlight.name()};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: {widget_bg.name()};
        }}
        
        QTextEdit {{
            background-color: {darker_bg.name()};
            border: 1px solid {border_color.name()};
            border-radius: 4px;
            padding: 4px;
            color: {text_color.name()};
        }}
        
        QTextEdit:focus {{
            border: 1px solid {highlight.name()};
        }}
        
        QFrame[frameShape="4"] {{
            color: {border_color.name()};
            background-color: {border_color.name()};
        }}
        
        QSplitter::handle {{
            background-color: {border_color.name()};
        }}
    """)
