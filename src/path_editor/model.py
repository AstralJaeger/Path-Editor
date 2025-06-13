import ctypes
import os
import subprocess
from typing import List, Tuple, Union
from subprocess import CompletedProcess


class PathModel:
    """
    Model class for handling PATH environment variables data.
    """
    def __init__(self, debug: bool = True):
        self.debug = debug
        self.user_paths: List[str] = []
        self.system_paths: List[str] = []
        self.applications: List[str] = []  # Combined list for backward compatibility
        self.reload_path()

    def reload_path(self) -> None:
        """
        Reload PATH environment variables from the OS.
        """
        self.user_paths, self.system_paths = self.get_path_from_os()

    def get_path_from_os(self) -> Tuple[List[str], List[str]]:
        """
        Get PATH environment variables from the OS.

        Returns:
            Tuple containing USER paths and SYSTEM paths
        """
        # Get SYSTEM path
        system_completed = self.run_command('[Environment]::GetEnvironmentVariable(\'Path\',\'Machine\')')
        system_completed.check_returncode()

        system_env_path = str(system_completed.stdout)
        system_env_path = system_env_path[2:-1]
        system_env_path = system_env_path.replace('\\r\\n', '')
        system_env_path = system_env_path.replace('\\\\', '/')
        system_env_path = system_env_path.lower()
        system_apps: List[str] = system_env_path.split(';')

        # Get USER path
        user_completed = self.run_command('[Environment]::GetEnvironmentVariable(\'Path\',\'User\')')
        user_completed.check_returncode()

        user_env_path = str(user_completed.stdout)
        user_env_path = user_env_path[2:-1]
        user_env_path = user_env_path.replace('\\r\\n', '')
        user_env_path = user_env_path.replace('\\\\', '/')
        user_env_path = user_env_path.lower()
        user_apps: List[str] = user_env_path.split(';')

        # For backward compatibility, keep applications as the combined list
        self.applications = system_apps + user_apps

        return user_apps, system_apps

    def set_path_to_os(self, user_path: List[str] = None, system_path: List[str] = None) -> bool:
        """
        Set the PATH environment variable in the OS.

        Args:
            user_path: List of paths to set for the USER path
            system_path: List of paths to set for the SYSTEM path

        Returns:
            True if successful, False if admin privileges are required for SYSTEM path

        If system_path is provided, admin privileges are required to set it.
        """
        success = True

        if user_path is not None:
            # Normalize paths before saving to ensure consistency with how they're loaded
            normalized_user_path = [self.normalize_path(path) for path in user_path]
            user_command = f'[Environment]::SetEnvironmentVariable("Path", \'{";".join(normalized_user_path)}\', [System.EnvironmentVariableTarget]::User)'
            print(f"Setting USER path: {user_command}")
            if not self.debug:
                self.run_command(user_command)

        if system_path is not None:
            if self.is_admin():
                # Normalize paths before saving to ensure consistency with how they're loaded
                normalized_system_path = [self.normalize_path(path) for path in system_path]
                system_command = f'[Environment]::SetEnvironmentVariable("Path", \'{";".join(normalized_system_path)}\', [System.EnvironmentVariableTarget]::Machine)'
                print(f"Setting SYSTEM path: {system_command}")
                if not self.debug:
                    self.run_command(system_command)
            else:
                print("Admin privileges required to set SYSTEM path")
                success = False

        return success

    def run_command(self, command: str) -> Union[CompletedProcess, CompletedProcess[bytes]]:
        """
        Run a PowerShell command.

        Args:
            command: PowerShell command to run

        Returns:
            CompletedProcess object with the command result
        """
        return subprocess.run(['powershell.exe', command], capture_output=True)

    def is_admin(self) -> bool:
        """
        Check if the application is running with admin privileges.

        Returns:
            True if running as admin, False otherwise
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def get_duplicate_count(self, paths: List[str]) -> int:
        """
        Count duplicates in a list of paths.

        Args:
            paths: List of paths to check

        Returns:
            Number of duplicate entries
        """
        unique_paths = set(paths)
        duplicates = len(paths) - len(unique_paths)
        return duplicates

    def get_filecount(self, directory: str) -> int:
        """
        Count files in a directory.

        Args:
            directory: Directory to count files in

        Returns:
            Number of files in the directory
        """
        try:
            return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])
        except:
            return 0

    def get_path_length(self, paths: List[str]) -> int:
        """
        Calculate the total length of all paths.

        Args:
            paths: List of paths

        Returns:
            Total length of all paths
        """
        return sum(map(lambda path: len(path), paths))

    def path_exists(self, path_str: str) -> bool:
        """
        Check if a path exists.

        Args:
            path_str: Path to check

        Returns:
            True if the path exists, False otherwise
        """
        return os.path.exists(path_str)

    def normalize_path(self, path_str: str) -> str:
        """
        Normalize a path string.

        Args:
            path_str: Path to normalize

        Returns:
            Normalized path
        """
        path_str = str(path_str)
        path_str = path_str.replace('\\r\\n', '')
        path_str = path_str.replace('\\\\', '/')
        path_str = path_str.replace('\\', '/')
        path_str = path_str.lower()
        return path_str
