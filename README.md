# PGChess

Python chess GUI using PyGame and Sunfish

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

### To Test

```bash
python -m pytest tests/ -v
```

### To Build

Use the build script that automatically detects your platform:

```bash
python build.py
```

This will create an executable in the `dist/` folder:
- **Windows:** Single-file executable `dist/PGChess.exe`
- **macOS:** App bundle `dist/PGChess.app` (drag to Applications folder)