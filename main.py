import ctypes
import os
import sys
import subprocess
import tkinter as tk
import tkinter.ttk
import collections

from typing import List, Union, Tuple
from os import path, listdir
from subprocess import CompletedProcess
from tkinter import *
from tkinter import ttk

debug = True
applications: List[str] = []
treeview: ttk.Treeview
duplicates_label: Label
total_entries_label: Label
total_length_label: Label


def main():
    # create window
    main_window = create_window()
    create_widgets(main_window)

    # Start tk loop
    main_window.mainloop()


def create_window() -> Tk:
    # print(f'Creating Window {tk.TkVersion}')
    return Tk()


def add_entry():
    pass


def edit_entry():
    pass


def remove_entry():
    global treeview
    selected = treeview.focus()
    if not selected:
        return
    treeview.delete(selected)
    applications.remove(treeview.item(selected)['values'][0])
    update_statistics()


def up_entry():
    global treeview
    selected = treeview.focus()
    index = treeview.index(selected)
    if index == 0:
        return
    treeview.move(selected, treeview.parent(selected), index - 1)
    applications[index], applications[index - 1] = applications[index - 1], applications[index]


def down_entry():
    global treeview
    selected = treeview.focus()
    index = treeview.index(selected)
    if index == len(treeview.get_children()) - 1:
        return
    treeview.move(selected, treeview.parent(selected), index + 1)
    applications[index], applications[index + 1] = applications[index + 1], applications[index]


def reload_path():
    global treeview
    treeview.delete(*treeview.get_children())
    for app in get_path_from_os():
        exists = path.exists(app)
        filecount = (get_filecount(app) if exists else 0)
        system = 'windows/system32' in app
        data = (app, filecount)
        treeview.insert('', tk.END, values=data, tags=[
            ('exists' if exists else 'nexists'),
            ('sys32' if system else 'nsys32')
        ])
    update_statistics()


def save_path():
    pass


def remove_duplicates():
    global applications, treeview
    duplicates: list[str] = [item for item, count in collections.Counter(applications).items() if count > 1]
    for index, child in enumerate(reversed(treeview.get_children())):
        item = treeview.item(child)
        value = item['values'][0]
        if value in duplicates:
            duplicates.remove(value)
            treeview.delete(child)
            applications.remove(value)
    update_statistics()


def remove_dead():
    global treeview
    for child in treeview.get_children(''):
        item = treeview.item(child)
        if 'nexists' in item['tags']:
            treeview.delete(child)
            applications.remove(item['values'][0])
    update_statistics()


def create_widgets(window: Tk) -> None:
    window.title('AstralJaeger\'s path editor v1.0.0')
    window.geometry('640x480')
    window.grid_columnconfigure(0, weight=2)
    window.grid_columnconfigure(2, weight=1)
    columns = ('path', 'filecount')

    global treeview, duplicates_label, total_entries_label, total_length_label
    treeview = ttk.Treeview(window, columns=columns, show='headings', selectmode='browse')
    treeview.heading('path', text='Path')
    treeview.heading('filecount', text='Filecount')

    treeview.tag_configure('nexists', background='orange')
    treeview.tag_configure('sys32', foreground='gray')

    treeview.place(relx=0.05, rely=0.05, relwidth=0.75, relheight=0.75)

    scrollbar = Scrollbar(window, orient=tk.VERTICAL, command=treeview.yview)
    treeview.configure(yscroll=scrollbar.set)
    scrollbar.place(relx=0.8, rely=0.05, relwidth=0.025, relheight=0.75)

    # Duplicates label
    duplicates_label = Label(text=f'Duplicates: {get_duplicate_count(applications)}')
    duplicates_label.place(relx=0.05, rely=0.825, relwidth=0.75, relheight=0.05)

    # Remove duplicates
    remove_duplicates_btn = Button(text='RM Duplicate', command=remove_duplicates)
    remove_duplicates_btn.place(relx=0.85, rely=0.825, relwidth=0.125, relheight=0.05)

    # Remove non-existent entries
    remove_nonexistent_btn = Button(text='RM Dead', command=remove_dead)
    remove_nonexistent_btn.place(relx=0.85, rely=0.885, relwidth=0.125, relheight=0.05)

    # Total count label
    total_entries_label = Label(text=f'Total entries: {len(applications)}')
    total_entries_label.place(relx=0.05, rely=0.885, relwidth=0.75, relheight=0.05)

    # Total length label
    total_length_label = Label(text=f'Total Length: {get_path_length(applications)}')
    total_length_label.place(relx=0.05, rely=0.945, relwidth=0.75, relheight=0.05)

    # -----
    # Add entry
    add_entry_btn = Button(text='Add', command=add_entry)
    add_entry_btn.place(relx=0.85, rely=0.05, relwidth=0.125, relheight=0.05)

    # Edit entry
    edit_entry_btn = Button(text='Edit', command=edit_entry)
    edit_entry_btn.place(relx=0.85, rely=0.11, relwidth=0.125, relheight=0.05)

    # Remove entry
    remove_entry_btn = Button(text='Remove', command=remove_entry)
    remove_entry_btn.place(relx=0.85, rely=0.17, relwidth=0.125, relheight=0.05)

    # -----
    # Move entry up
    up_btn = Button(text='Up', command=up_entry)
    up_btn.place(relx=0.85, rely=0.30, relwidth=0.125, relheight=0.05)

    # Move entry down
    down_btn = Button(text='Down', command=down_entry)
    down_btn.place(relx=0.85, rely=0.36, relwidth=0.125, relheight=0.05)

    # -----
    # Reload path
    reload_btn = Button(text='Reload', command=reload_path)
    reload_btn.place(relx=0.85, rely=0.49, relwidth=0.125, relheight=0.05)

    # Save path
    save_btn = Button(text='Save', command=save_path)
    save_btn.place(relx=0.85, rely=0.55, relwidth=0.125, relheight=0.05)

    reload_path()


def item_selected(event):
    return


def destroy_window(window: tk.Tk):
    window.destroy()


def update_statistics():
    update_duplicate_count()
    update_total_entries_count()
    update_total_length()


def update_duplicate_count():
    global applications, duplicates_label
    duplicates_label['text'] = f'Duplicates found: {get_duplicate_count(applications)}'


def update_total_entries_count():
    global applications, total_entries_label
    total_entries_label['text'] = f'Total entries: {len(applications)}'


def update_total_length():
    global applications, total_length_label
    total_length_label['text'] = f'Total length: {get_path_length(applications)}'


def get_duplicate_count(apps: List[str]) -> int:
    unique_apps = set(apps)
    duplicates = len(apps) - len(unique_apps)
    return duplicates


def get_filecount(dir: str):
    return len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])


def get_path_length(apps: List[str]) -> int:
    return sum(map(lambda app: len(app), apps))


def get_path_from_os() -> List[str]:
    completed = run_command('[Environment]::GetEnvironmentVariable(\'Path\',\'Machine\')')
    completed.check_returncode()

    env_path = str(completed.stdout)
    env_path = env_path[2:-1]
    env_path = env_path.replace('\\r\\n', '')
    env_path = env_path.replace('\\\\', '/')
    env_path = env_path.lower()
    global applications
    apps: List[str] = env_path.split(';')

    applications = apps
    return applications


def run_command(command: str) -> Union[CompletedProcess, CompletedProcess[bytes]]:
    return subprocess.run(['powershell.exe', command], capture_output=True)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == '__main__':
    if debug or is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join(sys.argv), None, 1)
