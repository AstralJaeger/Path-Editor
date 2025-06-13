import tkinter as tk
import sys
import os
import ctypes
from src.path_editor.model import PathModel
from src.path_editor.view import PathView
from src.path_editor.controller import PathController


def main():
    # Create the model
    model = PathModel(debug=True)

    # Create the view (with a new Tkinter root window)
    root = tk.Tk()
    view = PathView(root)

    # Create the controller (connects model and view)
    controller = PathController(model, view)

    # Start the Tkinter event loop
    root.mainloop()


def restart_with_admin():
    """
    Restart the application with administrator privileges.
    """
    # Get the path to the current Python executable and script
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)

    # Use ctypes to elevate privileges
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:  # Not admin
        # ShellExecute parameters: hwnd, operation, file, parameters, directory, show_cmd
        ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, f'"{script_path}"', None, 1)


if __name__ == '__main__':
    main()
