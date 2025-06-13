import collections
import tkinter as tk
from tkinter import messagebox

from model import PathModel
from view import PathView


class PathController:
    """
    Controller class for the PATH editor application.
    Connects the model and view components.
    """
    def __init__(self, model: PathModel, view: PathView):
        """
        Initialize the controller with model and view.

        Args:
            model: The PathModel instance
            view: The PathView instance
        """
        self.model = model
        self.view = view
        self.selected_path = ''
        self.selected_path_type = 'user'  # Default to 'user' or 'system'

        # Initialize the view
        self.view.create_widgets(self.item_selected)

        # Create command bindings
        self._create_command_bindings()

        self.reload_path()

    def _create_command_bindings(self):
        """Create command bindings for the view buttons."""
        commands = {
            'add': self.add_entry,
            'edit': self.edit_entry,
            'remove': self.remove_entry,
            'up': self.up_entry,
            'down': self.down_entry,
            'reload': self.reload_path,
            'save_user': self.save_user_path,
            'save_system': self.save_system_path,
            'save_both': self.save_path,
            'remove_duplicates': self.remove_duplicates,
            'remove_dead': self.remove_dead
        }
        self.view.bind_commands(commands)

    def item_selected(self, event):
        """
        Handle item selection in the treeview.

        Args:
            event: The selection event
        """
        sel_item = self.view.treeview.item(self.view.treeview.focus())

        # Check if this is a header item (parent node)
        if sel_item['text'] in ['USER PATH', 'SYSTEM PATH']:
            self.selected_path = ''
            self.selected_path_type = sel_item['text'].split()[0].lower()  # 'user' or 'system'
            return

        # Check if this is a path item
        if hasattr(sel_item, 'values') and len(sel_item['values']) >= 1:
            self.selected_path = sel_item['values'][0]

            # Determine if this is a USER or SYSTEM path
            tags = sel_item['tags']
            if 'user_path' in tags:
                self.selected_path_type = 'user'
            elif 'system_path' in tags:
                self.selected_path_type = 'system'
            else:
                # Default to user if not specified
                self.selected_path_type = 'user'

    def add_entry(self):
        """Show dialog for adding a new path entry."""
        ok_button = self.view.show_add_dialog(self.selected_path_type, self.model.is_admin())
        ok_button.config(command=self.confirm_add)

    def confirm_add(self):
        """Process the add dialog and add a new path entry."""
        filepath = self.view.get_add_path()

        if not self.model.path_exists(filepath):
            self.view.set_add_error('Path does not exist!')
            return
        else:
            self.view.set_add_error('')

        # Check if user has admin privileges for SYSTEM path
        path_type = self.view.add_path_type.get()
        if path_type == 'system' and not self.model.is_admin():
            self.view.set_add_error('Admin privileges required to modify SYSTEM path!')
            return

        filepath = self.model.normalize_path(filepath)
        filecount = self.model.get_filecount(filepath) if self.model.path_exists(filepath) else 0
        data = (filepath, filecount)

        # Find the parent node for the selected path type
        parent_nodes = [child for child in self.view.treeview.get_children() 
                        if self.view.treeview.item(child)['text'] in ['USER PATH', 'SYSTEM PATH']]
        parent_node = ''
        for node in parent_nodes:
            if self.view.treeview.item(node)['text'] == f"{path_type.upper()} PATH":
                parent_node = node
                break

        # Insert the new entry under the appropriate parent node
        self.view.treeview.insert(parent_node, tk.END, values=data, tags=[
            ('exists' if self.model.path_exists(filepath) else 'nexists'),
            ('sys32' if 'windows/system32' in filepath else 'nsys32'),
            ('empty' if filecount == 0 else 'nempty'),
            f'{path_type}_path'
        ])

        # Add to the appropriate path list
        if path_type == 'user':
            self.model.user_paths.append(filepath)
        else:  # system
            self.model.system_paths.append(filepath)

        # For backward compatibility
        self.model.applications.append(filepath)

        self.update_statistics()
        self.view.close_add_dialog()

    def edit_entry(self):
        """Show dialog for editing a path entry."""
        if not self.selected_path:
            return

        ok_button = self.view.show_edit_dialog(self.selected_path, self.selected_path_type, self.model.is_admin())
        ok_button.config(command=self.confirm_edit)

    def confirm_edit(self):
        """Process the edit dialog and update the path entry."""
        filepath = self.view.get_edit_path()

        if not self.model.path_exists(filepath):
            self.view.set_edit_error('Path does not exist!')
            return
        else:
            self.view.set_edit_error('')

        # Check if user has admin privileges for SYSTEM path
        new_path_type = self.view.edit_path_type.get()
        if new_path_type == 'system' and not self.model.is_admin():
            self.view.set_edit_error('Admin privileges required to modify SYSTEM path!')
            return

        filepath = self.model.normalize_path(filepath)
        filecount = self.model.get_filecount(filepath) if self.model.path_exists(filepath) else 0
        data = (filepath, filecount)

        # Get the selected item and its parent
        selected_item = self.view.treeview.focus()
        old_item = self.view.treeview.item(selected_item)['values'][0]
        old_parent = self.view.treeview.parent(selected_item)

        # Find the parent node for the new path type
        parent_nodes = [child for child in self.view.treeview.get_children() 
                        if self.view.treeview.item(child)['text'] in ['USER PATH', 'SYSTEM PATH']]
        new_parent = ''
        for node in parent_nodes:
            if self.view.treeview.item(node)['text'] == f"{new_path_type.upper()} PATH":
                new_parent = node
                break

        # Remove from old path list
        if self.selected_path_type == 'user':
            if old_item in self.model.user_paths:
                self.model.user_paths.remove(old_item)
        else:  # system
            if old_item in self.model.system_paths:
                self.model.system_paths.remove(old_item)

        # Add to new path list
        if new_path_type == 'user':
            self.model.user_paths.append(filepath)
        else:  # system
            self.model.system_paths.append(filepath)

        # Update applications list for backward compatibility
        if old_item in self.model.applications:
            self.model.applications.remove(old_item)
        self.model.applications.append(filepath)

        # Delete the old item and insert the new one under the appropriate parent
        self.view.treeview.delete(selected_item)
        self.view.treeview.insert(new_parent, tk.END, values=data, tags=[
            ('exists' if self.model.path_exists(filepath) else 'nexists'),
            ('sys32' if 'windows/system32' in filepath else 'nsys32'),
            ('empty' if filecount == 0 else 'nempty'),
            f'{new_path_type}_path'
        ])

        # Update the selected path type
        self.selected_path_type = new_path_type

        self.update_statistics()
        self.view.close_edit_dialog()

    def remove_entry(self):
        """Remove the selected path entry."""
        # Get the selected item
        selected_item = self.view.treeview.focus()
        if not selected_item:
            return

        # Check if this is a header item (parent node)
        if self.view.treeview.item(selected_item)['text'] in ['USER PATH', 'SYSTEM PATH']:
            return

        # Get the path value and tags
        item_data = self.view.treeview.item(selected_item)
        if not item_data['values']:
            return

        path_value = item_data['values'][0]
        tags = item_data['tags']

        # Check if user has admin privileges for SYSTEM path
        if 'system_path' in tags and not self.model.is_admin():
            self.view.show_admin_required_message()
            return

        # Remove from the appropriate path list
        if 'user_path' in tags:
            if path_value in self.model.user_paths:
                self.model.user_paths.remove(path_value)
        elif 'system_path' in tags:
            if path_value in self.model.system_paths:
                self.model.system_paths.remove(path_value)

        # Remove from applications list for backward compatibility
        if path_value in self.model.applications:
            self.model.applications.remove(path_value)

        # Delete the item from the treeview
        self.view.treeview.delete(selected_item)
        self.update_statistics()

    def up_entry(self):
        """Move the selected path entry up in the list."""
        # Get the selected item
        selected_item = self.view.treeview.focus()
        if not selected_item:
            return

        # Check if this is a header item (parent node)
        if self.view.treeview.item(selected_item)['text'] in ['USER PATH', 'SYSTEM PATH']:
            return

        # Get the parent and index
        parent = self.view.treeview.parent(selected_item)
        index = self.view.treeview.index(selected_item)

        # Can't move up if already at the top
        if index == 0:
            return

        # Get the path value and tags
        item_data = self.view.treeview.item(selected_item)
        if not item_data['values']:
            return

        path_value = item_data['values'][0]
        tags = item_data['tags']

        # Check if user has admin privileges for SYSTEM path
        if 'system_path' in tags and not self.model.is_admin():
            self.view.show_admin_required_message()
            return

        # Move the item up in the treeview
        self.view.treeview.move(selected_item, parent, index - 1)

        # Reorder in the appropriate path list
        if 'user_path' in tags:
            # Find the index in user_paths
            if path_value in self.model.user_paths:
                path_index = self.model.user_paths.index(path_value)
                if path_index > 0:
                    self.model.user_paths[path_index], self.model.user_paths[path_index - 1] = \
                        self.model.user_paths[path_index - 1], self.model.user_paths[path_index]
        elif 'system_path' in tags:
            # Find the index in system_paths
            if path_value in self.model.system_paths:
                path_index = self.model.system_paths.index(path_value)
                if path_index > 0:
                    self.model.system_paths[path_index], self.model.system_paths[path_index - 1] = \
                        self.model.system_paths[path_index - 1], self.model.system_paths[path_index]

        # For backward compatibility
        if path_value in self.model.applications:
            app_index = self.model.applications.index(path_value)
            if app_index > 0:
                self.model.applications[app_index], self.model.applications[app_index - 1] = \
                    self.model.applications[app_index - 1], self.model.applications[app_index]

    def down_entry(self):
        """Move the selected path entry down in the list."""
        # Get the selected item
        selected_item = self.view.treeview.focus()
        if not selected_item:
            return

        # Check if this is a header item (parent node)
        if self.view.treeview.item(selected_item)['text'] in ['USER PATH', 'SYSTEM PATH']:
            return

        # Get the parent and index
        parent = self.view.treeview.parent(selected_item)
        index = self.view.treeview.index(selected_item)

        # Get all siblings
        siblings = self.view.treeview.get_children(parent)

        # Can't move down if already at the bottom
        if index == len(siblings) - 1:
            return

        # Get the path value and tags
        item_data = self.view.treeview.item(selected_item)
        if not item_data['values']:
            return

        path_value = item_data['values'][0]
        tags = item_data['tags']

        # Check if user has admin privileges for SYSTEM path
        if 'system_path' in tags and not self.model.is_admin():
            self.view.show_admin_required_message()
            return

        # Move the item down in the treeview
        self.view.treeview.move(selected_item, parent, index + 1)

        # Reorder in the appropriate path list
        if 'user_path' in tags:
            # Find the index in user_paths
            if path_value in self.model.user_paths:
                path_index = self.model.user_paths.index(path_value)
                if path_index < len(self.model.user_paths) - 1:
                    self.model.user_paths[path_index], self.model.user_paths[path_index + 1] = \
                        self.model.user_paths[path_index + 1], self.model.user_paths[path_index]
        elif 'system_path' in tags:
            # Find the index in system_paths
            if path_value in self.model.system_paths:
                path_index = self.model.system_paths.index(path_value)
                if path_index < len(self.model.system_paths) - 1:
                    self.model.system_paths[path_index], self.model.system_paths[path_index + 1] = \
                        self.model.system_paths[path_index + 1], self.model.system_paths[path_index]

        # For backward compatibility
        if path_value in self.model.applications:
            app_index = self.model.applications.index(path_value)
            if app_index < len(self.model.applications) - 1:
                self.model.applications[app_index], self.model.applications[app_index + 1] = \
                    self.model.applications[app_index + 1], self.model.applications[app_index]

    def reload_path(self):
        """Reload PATH environment variables from the OS."""
        self.model.reload_path()
        self.view.populate_treeview(
            self.model.user_paths, 
            self.model.system_paths, 
            self.model.get_filecount, 
            self.model.path_exists
        )
        self.update_statistics()

    def save_user_path(self):
        """Save only the USER path."""
        self.model.set_path_to_os(user_path=self.model.user_paths)

    def save_system_path(self):
        """Save only the SYSTEM path."""
        if not self.model.is_admin():
            if self.view.show_admin_required_message():
                # User wants to restart with elevated permissions
                self.view.root.destroy()  # Close the current instance
                import main
                main.restart_with_admin()
            return
        self.model.set_path_to_os(system_path=self.model.system_paths)

    def save_path(self):
        """Save both USER and SYSTEM paths."""
        success = self.model.set_path_to_os(
            user_path=self.model.user_paths, 
            system_path=self.model.system_paths
        )
        if not success:
            if self.view.show_admin_required_message():
                # User wants to restart with elevated permissions
                self.view.root.destroy()  # Close the current instance
                import main
                main.restart_with_admin()

    def remove_duplicates(self):
        """Remove duplicate path entries for the selected section."""
        # Find duplicates in USER paths
        user_duplicates = [item for item, count in collections.Counter(self.model.user_paths).items() if count > 1]

        # Find duplicates in SYSTEM paths
        system_duplicates = [item for item, count in collections.Counter(self.model.system_paths).items() if count > 1]

        # Find duplicates across both lists (paths that appear in both USER and SYSTEM)
        cross_duplicates = [item for item in self.model.user_paths if item in self.model.system_paths]

        # Process only the selected section
        selected_parents = []
        for parent in self.view.treeview.get_children():
            # Skip if this is not a parent node
            if self.view.treeview.item(parent)['text'] not in ['USER PATH', 'SYSTEM PATH']:
                continue

            # Only process the selected section
            parent_type = self.view.treeview.item(parent)['text'].split()[0].lower()  # 'user' or 'system'
            if parent_type == self.selected_path_type or not self.selected_path_type:
                selected_parents.append(parent)

        # If no section is selected, show a message and return
        if not selected_parents:
            messagebox.showinfo("Selection Required", "Please select a USER or SYSTEM path entry first.")
            return

        # Process selected parents
        for parent in selected_parents:
            is_user = self.view.treeview.item(parent)['text'] == 'USER PATH'

            # Check if we need admin privileges for SYSTEM path
            if not is_user and not self.model.is_admin():
                if self.view.show_admin_required_message():
                    # User wants to restart with elevated permissions
                    self.view.root.destroy()  # Close the current instance
                    import main
                    main.restart_with_admin()
                    return
                continue

            # Process children of this parent
            for child in reversed(self.view.treeview.get_children(parent)):
                item = self.view.treeview.item(child)
                if not item['values']:
                    continue

                value = item['values'][0]

                # Check if this is a duplicate
                if (is_user and value in user_duplicates) or (not is_user and value in system_duplicates) or value in cross_duplicates:
                    # Remove from the appropriate list
                    if is_user:
                        if value in user_duplicates:
                            user_duplicates.remove(value)
                        if value in self.model.user_paths:
                            self.model.user_paths.remove(value)
                    else:  # system
                        if value in system_duplicates:
                            system_duplicates.remove(value)
                        if value in self.model.system_paths:
                            self.model.system_paths.remove(value)

                    # Remove from cross_duplicates if it's there
                    if value in cross_duplicates:
                        cross_duplicates.remove(value)

                    # Remove from applications for backward compatibility
                    if value in self.model.applications:
                        self.model.applications.remove(value)

                    # Delete from treeview
                    self.view.treeview.delete(child)

        self.update_statistics()

    def remove_dead(self):
        """Remove non-existent path entries for the selected section."""
        # Process only the selected section
        selected_parents = []
        for parent in self.view.treeview.get_children():
            # Skip if this is not a parent node
            if self.view.treeview.item(parent)['text'] not in ['USER PATH', 'SYSTEM PATH']:
                continue

            # Only process the selected section
            parent_type = self.view.treeview.item(parent)['text'].split()[0].lower()  # 'user' or 'system'
            if parent_type == self.selected_path_type or not self.selected_path_type:
                selected_parents.append(parent)

        # If no section is selected, show a message and return
        if not selected_parents:
            messagebox.showinfo("Selection Required", "Please select a USER or SYSTEM path entry first.")
            return

        # Process selected parents
        for parent in selected_parents:
            is_user = self.view.treeview.item(parent)['text'] == 'USER PATH'

            # Check if we need admin privileges for SYSTEM path
            if not is_user and not self.model.is_admin():
                if self.view.show_admin_required_message():
                    # User wants to restart with elevated permissions
                    self.view.root.destroy()  # Close the current instance
                    import main
                    main.restart_with_admin()
                    return
                continue

            # Process children of this parent
            for child in reversed(self.view.treeview.get_children(parent)):
                item = self.view.treeview.item(child)
                if not item['values']:
                    continue

                # Check if this path doesn't exist
                if 'nexists' in item['tags']:
                    value = item['values'][0]

                    # Remove from the appropriate list
                    if is_user:
                        if value in self.model.user_paths:
                            self.model.user_paths.remove(value)
                    else:  # system
                        if value in self.model.system_paths:
                            self.model.system_paths.remove(value)

                    # Remove from applications for backward compatibility
                    if value in self.model.applications:
                        self.model.applications.remove(value)

                    # Delete from treeview
                    self.view.treeview.delete(child)

        self.update_statistics()

    def update_statistics(self):
        """Update statistics labels."""
        # Count duplicates in USER paths
        user_duplicates = self.model.get_duplicate_count(self.model.user_paths)

        # Count duplicates in SYSTEM paths
        system_duplicates = self.model.get_duplicate_count(self.model.system_paths)

        # Count duplicates across both lists (paths that appear in both USER and SYSTEM)
        cross_duplicates = len([item for item in self.model.user_paths if item in self.model.system_paths])

        # Calculate path lengths
        user_length = self.model.get_path_length(self.model.user_paths)
        system_length = self.model.get_path_length(self.model.system_paths)

        # Update statistics in the view
        self.view.update_statistics(
            user_duplicates, 
            system_duplicates, 
            cross_duplicates, 
            len(self.model.user_paths), 
            len(self.model.system_paths), 
            user_length, 
            system_length
        )
