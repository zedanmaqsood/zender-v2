import os

try:
    os.system('cmd /k "venv\Scripts\\activate & cls & main.py"')
except:
    print("Couldn't execute command.")