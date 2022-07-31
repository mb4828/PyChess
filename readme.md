# PyChess

Python implementation of chess using PyGame - Incomplete !

To setup:
```
venv/Scripts/activate
pip install requirements.txt
```

To run:
```
python main.py
```

To build:
```
pyinstaller --onefile main.py --paths venv/Lib/site-packages --paths game/ --paths logic/ --add-data "assets/images/*;assets/images" --add-data "assets/sounds/*;assets/sounds" --add-data "venv/
Lib/site-packages/pygame_menu/resources/fonts/*;pygame_menu/resources/fonts" --name PyChess --icon pychess.ico --noconsole
```