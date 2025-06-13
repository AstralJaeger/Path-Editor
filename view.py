import tkinter as tk
from tkinter import Tk, Label, Button, Frame, Text, StringVar, Scrollbar, Radiobutton, LEFT
from tkinter import ttk, messagebox


class PathView:
    """
    View class for the PATH editor application.
    """
    def __init__(self, root: Tk):
        """
        Initialize the view with the root window.

        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.setup_window()

        # UI components
        self.treeview = None
        self.duplicates_label = None
        self.total_entries_label = None
        self.total_length_label = None

        # Popup windows and their components
        self.add_popup = None
        self.add_text = None
        self.add_error_label = None
        self.add_path_type = None

        self.edit_popup = None
        self.edit_text = None
        self.edit_error_label = None
        self.edit_path_type = None

    def setup_window(self):
        """Set up the main window properties."""
        self.root.title('AstralJaeger\'s path editor v2.0.0 - USER & SYSTEM Path Manager')
        self.root.geometry('640x480')
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(2, weight=1)

    def create_widgets(self, item_selected_callback):
        """
        Create all widgets for the main window.

        Args:
            item_selected_callback: Callback function for when an item is selected
        """
        columns = ('path', 'filecount')

        # Create treeview
        self.treeview = ttk.Treeview(self.root, columns=columns, show='tree headings', selectmode='browse')
        self.treeview.heading('path', text='Path')
        self.treeview.heading('filecount', text='Filecount')
        self.treeview.column('#0', width=120)  # Width for the tree column

        # Configure tags
        self.treeview.tag_configure('nexists', background='orange')
        self.treeview.tag_configure('empty', background='lightblue')
        self.treeview.tag_configure('sys32', foreground='gray')
        self.treeview.tag_configure('header', font=('Arial', 10, 'bold'))
        self.treeview.tag_configure('user_path', foreground='blue')
        self.treeview.tag_configure('system_path', foreground='green')

        self.treeview.place(relx=0.05, rely=0.05, relwidth=0.75, relheight=0.75)

        # Add scrollbar
        scrollbar = Scrollbar(self.root, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.8, rely=0.05, relwidth=0.025, relheight=0.75)

        # Bind selection event
        self.treeview.bind('<ButtonRelease-1>', item_selected_callback)

        # Statistics labels
        self.duplicates_label = Label(self.root, text='Duplicates: 0')
        self.duplicates_label.place(relx=0.05, rely=0.825, relwidth=0.75, relheight=0.05)

        self.total_entries_label = Label(self.root, text='Total entries: 0')
        self.total_entries_label.place(relx=0.05, rely=0.885, relwidth=0.75, relheight=0.05)

        self.total_length_label = Label(self.root, text='Total Length: 0')
        self.total_length_label.place(relx=0.05, rely=0.945, relwidth=0.75, relheight=0.05)

        # Buttons for path management
        self._create_buttons()

    def _create_buttons(self):
        """Create all buttons for the main window."""
        # Path entry management buttons
        add_entry_btn = Button(self.root, text='Add')
        add_entry_btn.place(relx=0.85, rely=0.05, relwidth=0.125, relheight=0.05)

        edit_entry_btn = Button(self.root, text='Edit')
        edit_entry_btn.place(relx=0.85, rely=0.11, relwidth=0.125, relheight=0.05)

        remove_entry_btn = Button(self.root, text='Remove')
        remove_entry_btn.place(relx=0.85, rely=0.17, relwidth=0.125, relheight=0.05)

        # Entry movement buttons
        up_btn = Button(self.root, text='Up')
        up_btn.place(relx=0.85, rely=0.30, relwidth=0.125, relheight=0.05)

        down_btn = Button(self.root, text='Down')
        down_btn.place(relx=0.85, rely=0.36, relwidth=0.125, relheight=0.05)

        # Path management buttons
        reload_btn = Button(self.root, text='Reload')
        reload_btn.place(relx=0.85, rely=0.49, relwidth=0.125, relheight=0.05)

        save_user_btn = Button(self.root, text='Save USER')
        save_user_btn.place(relx=0.85, rely=0.55, relwidth=0.125, relheight=0.05)

        save_system_btn = Button(self.root, text='Save SYSTEM')
        save_system_btn.place(relx=0.85, rely=0.61, relwidth=0.125, relheight=0.05)

        save_both_btn = Button(self.root, text='Save Both')
        save_both_btn.place(relx=0.85, rely=0.67, relwidth=0.125, relheight=0.05)

        # Cleanup buttons
        remove_duplicates_btn = Button(self.root, text='RM Duplicate')
        remove_duplicates_btn.place(relx=0.85, rely=0.825, relwidth=0.125, relheight=0.05)

        remove_nonexistent_btn = Button(self.root, text='RM Dead')
        remove_nonexistent_btn.place(relx=0.85, rely=0.885, relwidth=0.125, relheight=0.05)

        # Store buttons as attributes for later command binding
        self.add_btn = add_entry_btn
        self.edit_btn = edit_entry_btn
        self.remove_btn = remove_entry_btn
        self.up_btn = up_btn
        self.down_btn = down_btn
        self.reload_btn = reload_btn
        self.save_user_btn = save_user_btn
        self.save_system_btn = save_system_btn
        self.save_both_btn = save_both_btn
        self.remove_duplicates_btn = remove_duplicates_btn
        self.remove_nonexistent_btn = remove_nonexistent_btn

    def bind_commands(self, commands):
        """
        Bind command callbacks to buttons.

        Args:
            commands: Dictionary of command callbacks
        """
        self.add_btn.config(command=commands.get('add', lambda: None))
        self.edit_btn.config(command=commands.get('edit', lambda: None))
        self.remove_btn.config(command=commands.get('remove', lambda: None))
        self.up_btn.config(command=commands.get('up', lambda: None))
        self.down_btn.config(command=commands.get('down', lambda: None))
        self.reload_btn.config(command=commands.get('reload', lambda: None))
        self.save_user_btn.config(command=commands.get('save_user', lambda: None))
        self.save_system_btn.config(command=commands.get('save_system', lambda: None))
        self.save_both_btn.config(command=commands.get('save_both', lambda: None))
        self.remove_duplicates_btn.config(command=commands.get('remove_duplicates', lambda: None))
        self.remove_nonexistent_btn.config(command=commands.get('remove_dead', lambda: None))

    def update_statistics(self, user_duplicates, system_duplicates, cross_duplicates, 
                         user_count, system_count, user_length, system_length):
        """
        Update statistics labels.

        Args:
            user_duplicates: Number of duplicates in USER path
            system_duplicates: Number of duplicates in SYSTEM path
            cross_duplicates: Number of duplicates across USER and SYSTEM paths
            user_count: Number of USER path entries
            system_count: Number of SYSTEM path entries
            user_length: Total length of USER path entries
            system_length: Total length of SYSTEM path entries
        """
        total_duplicates = user_duplicates + system_duplicates + cross_duplicates
        self.duplicates_label['text'] = f'Duplicates found: {total_duplicates} (USER: {user_duplicates}, SYSTEM: {system_duplicates}, Cross: {cross_duplicates})'
        self.total_entries_label['text'] = f'Total entries: {user_count + system_count} (USER: {user_count}, SYSTEM: {system_count})'
        self.total_length_label['text'] = f'Total length: {user_length + system_length} (USER: {user_length}, SYSTEM: {system_length})'

    def populate_treeview(self, user_paths, system_paths, get_filecount_callback, path_exists_callback):
        """
        Populate the treeview with path entries.

        Args:
            user_paths: List of USER path entries
            system_paths: List of SYSTEM path entries
            get_filecount_callback: Callback to get file count for a path
            path_exists_callback: Callback to check if a path exists
        """
        # Clear existing items
        self.treeview.delete(*self.treeview.get_children())

        # Create a parent node for USER paths
        user_parent = self.treeview.insert('', tk.END, text='USER PATH', open=True, tags=['header'])

        # Add USER paths
        for app in user_paths:
            exists = path_exists_callback(app)
            filecount = get_filecount_callback(app) if exists else 0
            system = 'windows/system32' in app
            data = (app, filecount)
            self.treeview.insert(user_parent, tk.END, values=data, tags=[
                ('exists' if exists else 'nexists'),
                ('sys32' if system else 'nsys32'),
                ('empty' if filecount == 0 else 'nempty'),
                'user_path'
            ])

        # Create a parent node for SYSTEM paths
        system_parent = self.treeview.insert('', tk.END, text='SYSTEM PATH', open=True, tags=['header'])

        # Add SYSTEM paths
        for app in system_paths:
            exists = path_exists_callback(app)
            filecount = get_filecount_callback(app) if exists else 0
            system = 'windows/system32' in app
            data = (app, filecount)
            self.treeview.insert(system_parent, tk.END, values=data, tags=[
                ('exists' if exists else 'nexists'),
                ('sys32' if system else 'nsys32'),
                ('empty' if filecount == 0 else 'nempty'),
                'system_path'
            ])

    def show_add_dialog(self, path_type, is_admin):
        """
        Show dialog for adding a new path entry.

        Args:
            path_type: Current path type ('user' or 'system')
            is_admin: Whether the application is running with admin privileges

        Returns:
            The add dialog window
        """
        self.add_popup = tk.Toplevel(self.root)
        self.add_popup.wm_title('Add item')

        label = Label(self.add_popup, text='Path:')
        label.grid(column=0, row=0)

        self.add_text = Text(self.add_popup, height=1)
        self.add_text.grid(column=1, row=0, rowspan=2)

        self.add_error_label = Label(self.add_popup)
        self.add_error_label.grid(column=0, row=1, rowspan=4)

        # Radio buttons for path type
        self.add_path_type = StringVar(value=path_type)

        path_type_frame = Frame(self.add_popup)
        path_type_frame.grid(column=1, row=2, sticky='w')

        user_radio = Radiobutton(path_type_frame, text="USER Path", variable=self.add_path_type, value="user")
        user_radio.pack(side=LEFT)

        system_radio = Radiobutton(path_type_frame, text="SYSTEM Path", variable=self.add_path_type, value="system")
        system_radio.pack(side=LEFT)

        # If not admin, disable SYSTEM path option
        if not is_admin and path_type == 'system':
            system_radio.config(state=tk.DISABLED)
            self.add_path_type.set("user")
            self.add_error_label['text'] = 'Admin privileges required to modify SYSTEM path'

        button = Button(self.add_popup, text='OK')
        button.grid(column=3, row=0)

        return button

    def show_edit_dialog(self, selected_path, path_type, is_admin):
        """
        Show dialog for editing a path entry.

        Args:
            selected_path: Currently selected path
            path_type: Current path type ('user' or 'system')
            is_admin: Whether the application is running with admin privileges

        Returns:
            The edit dialog window
        """
        self.edit_popup = tk.Toplevel(self.root)
        self.edit_popup.wm_title('Edit item')

        label = Label(self.edit_popup, text='Path:')
        label.grid(column=0, row=0)

        self.edit_text = Text(self.edit_popup, height=1)
        self.edit_text.grid(column=1, row=0, rowspan=2)
        self.edit_text.insert(1.0, selected_path)

        self.edit_error_label = Label(self.edit_popup)
        self.edit_error_label.grid(column=0, row=1, rowspan=4)

        # Radio buttons for path type
        self.edit_path_type = StringVar(value=path_type)

        path_type_frame = Frame(self.edit_popup)
        path_type_frame.grid(column=1, row=2, sticky='w')

        user_radio = Radiobutton(path_type_frame, text="USER Path", variable=self.edit_path_type, value="user")
        user_radio.pack(side=LEFT)

        system_radio = Radiobutton(path_type_frame, text="SYSTEM Path", variable=self.edit_path_type, value="system")
        system_radio.pack(side=LEFT)

        # If not admin and trying to edit SYSTEM path, disable SYSTEM option
        if not is_admin and path_type == 'system':
            system_radio.config(state=tk.DISABLED)
            self.edit_error_label['text'] = 'Admin privileges required to modify SYSTEM path'

        button = Button(self.edit_popup, text='OK')
        button.grid(column=3, row=0)

        return button

    def show_admin_required_message(self):
        """Show a message that admin privileges are required and offer to restart with elevated permissions."""
        result = messagebox.askyesno(
            "Admin privileges required", 
            "You need to run this application as administrator to save the SYSTEM path.\n\nDo you want to restart the application with administrator privileges?",
            icon='warning'
        )

        if result:
            # Return True to indicate that the user wants to restart with elevated permissions
            return True
        return False

    def get_add_path(self):
        """Get the path from the add dialog."""
        return self.add_text.get(1.0, "end-1c")

    def get_edit_path(self):
        """Get the path from the edit dialog."""
        return self.edit_text.get(1.0, "end-1c")

    def set_add_error(self, error_text):
        """Set error text in the add dialog."""
        self.add_error_label['text'] = error_text

    def set_edit_error(self, error_text):
        """Set error text in the edit dialog."""
        self.edit_error_label['text'] = error_text

    def close_add_dialog(self):
        """Close the add dialog."""
        if self.add_popup:
            self.add_popup.destroy()

    def close_edit_dialog(self):
        """Close the edit dialog."""
        if self.edit_popup:
            self.edit_popup.destroy()
