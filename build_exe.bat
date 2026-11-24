@REM  conda activate yolo_env
pyinstaller --noconsole --onefile --icon="ui/ICO.png" --add-data "ui/Bosch-Logo.png;ui" --add-data "ui/ICO.png;ui" --add-data "ui/main.ui;ui" app.py