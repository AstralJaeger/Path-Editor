# Path Editor

A Windows utility for managing PATH environment variables. This tool allows you to view, edit, and clean up both USER and SYSTEM PATH variables.

![Path Editor Screenshot](https://github.com/user/path-editor/raw/main/docs/screenshot.png)

## Features

- View and edit both USER and SYSTEM PATH variables
- Add, edit, and remove path entries
- Move entries up and down to change priority
- Remove duplicate entries
- Remove non-existent (dead) paths
- View statistics about your PATH variables
- Requires admin privileges only for SYSTEM PATH modifications

## Installation

### Download the Executable

1. Go to the [Releases](https://github.com/user/path-editor/releases) page
2. Download the latest `path-editor.exe` file
3. Run the executable (no installation required)

### Build from Source

1. Clone the repository
2. Install dependencies with uv: `uv pip install -e .`
3. Run the application: `python main.py`

## Usage

### Basic Navigation

- The treeview displays both USER and SYSTEM PATH entries
- Select an entry to edit, remove, or move it
- Use the buttons on the right to perform actions

### Adding a Path

1. Select either the USER or SYSTEM section in the treeview
2. Click the "Add" button
3. Enter the path in the dialog
4. Select the path type (USER or SYSTEM)
5. Click "OK"

### Editing a Path

1. Select the path entry you want to edit
2. Click the "Edit" button
3. Modify the path in the dialog
4. Optionally change the path type
5. Click "OK"

### Removing a Path

1. Select the path entry you want to remove
2. Click the "Remove" button
3. Confirm the deletion

### Cleaning Up Paths

1. Select either the USER or SYSTEM section in the treeview
2. Click "RM Duplicate" to remove duplicate entries in the selected section
3. Click "RM Dead" to remove non-existent paths in the selected section

### Saving Changes

- Click "Save USER" to save changes to the USER PATH
- Click "Save SYSTEM" to save changes to the SYSTEM PATH (requires admin privileges)
- Click "Save Both" to save changes to both

## Development

### Setup Development Environment

1. Clone the repository
2. Install development dependencies: `uv pip install -e ".[dev]"`
3. Run linting checks: `ruff check .`

### Building the Executable

```bash
pyinstaller --onefile --windowed --name path-editor main.py
```

### Creating a Release

1. Update the version in `pyproject.toml`
2. Create and push a new tag: `git tag v1.0.0 && git push --tags`
3. The GitHub Actions workflow will automatically build and create a release

## License

This project is licensed under the MIT License - see the LICENSE file for details.
