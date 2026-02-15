# PyChess

Python implementation of chess using PyGame - Incomplete !

### To Setup

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### To Run

Python 3.11 or above
```
venv/bin/python main.py
```

### To Build

Use the build script that automatically detects your platform:

```bash
python build.py
```

This will create an executable in the `dist/` folder:
- **Windows:** Single-file executable `dist/PyChess.exe`
- **macOS:** App bundle `dist/PyChess.app` (drag to Applications folder)