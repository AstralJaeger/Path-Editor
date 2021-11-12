import ctypes
import sys
import subprocess
import tkinter as tk

from typing import List, Union, Tuple
from os import path, listdir
from subprocess import CompletedProcess
from tkinter import *
from tkinter import ttk

debug = True


def main():
    # create window
    main_window = create_window()
    # print(f'Querying path from OS')
    applications = get_path_from_os()

    create_widgets(main_window, applications)

    not_found = 0
    for i, application in enumerate(applications):
        exists = path.exists(application)
        not_found += (1 if not exists else 0)
        # print(f'{i}. {application} - {"exists" if exists else "not found"}')

    # print(f'Unused entries: {not_found}')

    # Start tk loop
    main_window.mainloop()


def create_window() -> Tk:
    # print(f'Creating Window {tk.TkVersion}')
    return Tk()


def create_widgets(window: Tk, applications) -> None:
    window.title('AstralJaeger\' path editor v1.0.0')
    window.geometry('640x480')
    window.grid_columnconfigure(0, weight=2)
    window.grid_columnconfigure(2, weight=1)
    columns = ('path', )

    table = ttk.Treeview(window, columns=columns, show='headings')
    table.heading('path', text='Path')

    for app in applications:
        t = (app, )
        table.insert('', tk.END, values=t, tags=('exists' if path.exists(app) else 'nexists'))

    table.tag_configure('exists', background='white')
    table.tag_configure('nexists', background='orange')
    # table.bind('<<TreeviewSelect>>', item_selected)

    table.place(relx=0.05, rely=0.05, relwidth=0.75, relheight=0.75)

    scrollbar = Scrollbar(window, orient=tk.VERTICAL, command=table.yview)
    table.configure(yscroll=scrollbar.set)
    scrollbar.place(relx=0.8, rely=0.05, relwidth=0.025, relheight=0.75)

    # Duplicates label
    duplicates_label = Label(text=f'Duplicates: {get_duplicate_count(applications)}')
    duplicates_label.place(relx=0.05, rely=0.825, relwidth=0.75, relheight=0.05)

    # Remove duplicates
    remove_duplicates = Button(text='RM Duplicate')
    remove_duplicates.place(relx=0.85, rely=0.825, relwidth=0.125, relheight=0.05)

    # Remove non-existent entries
    remove_nonexistent = Button(text='RM Dead')
    remove_nonexistent.place(relx=0.85, rely=0.885, relwidth=0.125, relheight=0.05)

    # Total count label
    total_label = Label(text=f'Total entries: {len(applications)}')
    total_label.place(relx=0.05, rely=0.885, relwidth=0.75, relheight=0.05)

    # Add entry
    add_entry = Button(text='Add')
    add_entry.place(relx=0.85, rely=0.05, relwidth=0.125, relheight=0.05)

    # Remove entry
    remove_entry = Button(text='Remove')
    remove_entry.place(relx=0.85, rely=0.11, relwidth=0.125, relheight=0.05)

    # Move entry up
    up = Button(text='Up')
    up.place(relx=0.85, rely=0.17, relwidth=0.125, relheight=0.05)

    # Move entry down
    down = Button(text='Down')
    down.place(relx=0.85, rely=0.23, relwidth=0.125, relheight=0.05)

    # Reload path
    reload = Button(text='Reload')
    reload.place(relx=0.85, rely=0.45, relwidth=0.125, relheight=0.05)

    # Save path
    save = Button(text='Save')
    save.place(relx=0.85, rely=0.51, relwidth=0.125, relheight=0.05)


def item_selected(event):
    return


def destroy_window(window: tk.Tk):
    window.destroy()


def get_path_from_os() -> List[str]:
    completed = run_command('[Environment]::GetEnvironmentVariable(\'Path\',\'Machine\')')
    completed.check_returncode()

    env_path = str(completed.stdout)
    env_path = env_path[2:-1]
    env_path = env_path.replace('\\r\\n', '')
    env_path = env_path.replace('\\\\', '/')
    env_path = env_path.lower()
    applications: List[str] = env_path.split(';')
    return applications


def get_duplicate_count(applications: List[str]) -> int:
    unique_applications = set(applications)
    duplicates = len(applications) - len(unique_applications)
    # print(f'Duplicates found: {duplicates}')
    return duplicates


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_command(command: str) -> Union[CompletedProcess, CompletedProcess[bytes]]:
    return subprocess.run(['powershell.exe', command], capture_output=True)


if __name__ == '__main__':
    if debug or is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join(sys.argv), None, 1)
