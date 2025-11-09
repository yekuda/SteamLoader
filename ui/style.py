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