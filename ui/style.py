# --- STYLESHEETS ---

# Ana uygulama stili
MAIN_WINDOW_STYLE = '''
QWidget {
    background: #252622;  /* Koyu arka plan */
    color: #d0d0d0;       /* Açık gri metin rengi */
    font-family: 'Segoe UI'; /* Modern font */
}
QLabel {
    color: #d0d0d0;
}
QLineEdit {
    border: 2px solid #9c783e;  /* Altın rengi kenarlık */
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    background: #1d1e1a;        /* Daha koyu giriş alanı arka planı */
    color: #d0d0d0;
}
QPushButton {
    background: #9c783e;        /* Altın rengi buton */
    color: #f0f0f0;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background: #8a6a35;        /* Hover efekti için daha koyu altın rengi */
}
/* Silme butonu için özel stil */
QPushButton#deleteButton {
    background-color: #992e22; /* Koyu kırmızı */
}
QPushButton#deleteButton:hover {
    background-color: #80261d; /* Hover efekti için daha koyu kırmızı */
}
QMessageBox {
    background-color: #1d1e1a;
}
QMessageBox QLabel {
    color: #d0d0d0;
    font-size: 14px;
}
QMessageBox QPushButton {
    background: #9c783e;
    color: #f0f0f0;
    border-radius: 8px;
    padding: 6px 18px;
    font-size: 13px;
    font-weight: bold;
}
QMessageBox QPushButton:hover {
    background: #8a6a35;
}
'''

# Sürükle-bırak alanı stili
DRAG_DROP_AREA_STYLE = '''
QLabel {
    border: 3px dashed #9c783e;
    border-radius: 16px;
    background: #1d1e1a;
    color: #9c783e;
    font-size: 18px;
    font-weight: bold;
    padding: 40px;
    margin-top: 10px;
    margin-bottom: 10px;
}
QLabel:hover {
    background: #353632;
    color: #d0d0d0;
}
'''

# Oyunlar container stili
GAMES_CONTAINER_STYLE = '''
QWidget {
    background: transparent;
}
'''

# Liste widget stili
LIST_WIDGET_STYLE = '''
QListWidget {
    border: 2px solid #9c783e;
    border-radius: 8px;
    background: #1d1e1a;
    color: #d0d0d0;
    font-size: 13px;
    padding: 5px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px;
}
QListWidget::item:hover {
    background: #353632;
}
QScrollBar:vertical {
    border: none;
    background: #1d1e1a;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #9c783e;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #8a6a35;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
'''

# UI Components stilleri
TITLE_LABEL_STYLE = '''
    color: #9c783e;
    margin-bottom: 0px;
'''

DESCRIPTION_LABEL_STYLE = '''
    color: #b0b0b0;
    margin-bottom: 10px;
'''

SEPARATOR_LINE_STYLE = '''
    background-color: #9c783e;
'''

GAMES_LIST_TITLE_STYLE = '''
    color: #9c783e;
    font-weight: bold;
    font-size: 14px;
    padding: 0px;
    margin: 0px;
'''

# Drag drop hover stili
DRAG_DROP_HOVER_STYLE = '''
    QLabel {
        background: #353632;
    }
'''

# Dialog stilleri
GAMES_DIALOG_TITLE_STYLE = '''
    color: #9c783e;
    font-weight: bold;
    font-size: 22px;
    padding: 0px;
    margin: 0px;
'''

GAMES_DIALOG_SUBTITLE_STYLE = '''
    color: #b0b0b0;
    font-size: 13px;
    font-weight: bold;
    padding: 0px;
    margin: 0px;
'''

GAMES_DIALOG_SEPARATOR_STYLE = '''
    background-color: #9c783e;
    max-height: 2px;
    margin: 5px 0px;
'''

# Oyunlar dialog liste widget stili
GAMES_DIALOG_LIST_STYLE = '''
QListWidget {
    border: 2px solid #9c783e;
    border-radius: 12px;
    background: #1d1e1a;
    color: #d0d0d0;
    font-size: 14px;
    font-weight: bold;
    padding: 8px;
}
QListWidget::item {
    padding: 12px 15px;
    border-radius: 8px;
    margin: 4px 0px;
    background: #252622;
    border: 1px solid transparent;
    font-weight: bold;
}
QListWidget::item:hover {
    background: #353632;
    border: 1px solid #9c783e;
}
QScrollBar:vertical {
    border: none;
    background: #1d1e1a;
    width: 12px;
    border-radius: 6px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #9c783e;
    border-radius: 6px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #8a6a35;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
'''