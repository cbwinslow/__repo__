import os
import sys
import shutil
import platform
import logging
from pathlib import Path
from typing import List, Dict, Union, Optional, Generator
from datetime import datetime
import subprocess
from enum import Enum

class OSType(Enum):
    """Enumeration for supported operating systems"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "darwin"
    UNKNOWN = "unknown"

class SystemUtils:
    """
    A utility class providing cross-platform system operations and file handling.
    Implements common operations for both Windows and Linux environments.
    """
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Initialize the SystemUtils class with logging configuration.
        
        Args:
            log_level (int): Logging level (default: logging.INFO)
        """
        self._setup_logging(log_level)
        self.os_type = self._determine_os()
    
    def _setup_logging(self, log_level: int) -> None:
        """
        Configure logging for the utility class.
        
        Args:
            log_level (int): Desired logging level
        """
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _determine_os() -> OSType:
        """
        Determine the current operating system.
        
        Returns:
            OSType: Enum representing the current OS
        """
        system = platform.system().lower()
        if system == "windows":
            return OSType.WINDOWS
        elif system == "linux":
            return OSType.LINUX
        elif system == "darwin":
            return OSType.MACOS
        return OSType.UNKNOWN

    def is_windows(self) -> bool:
        """Check if current OS is Windows"""
        return self.os_type == OSType.WINDOWS

    def is_linux(self) -> bool:
        """Check if current OS is Linux"""
        return self.os_type == OSType.LINUX

    def is_macos(self) -> bool:
        """Check if current OS is macOS"""
        return self.os_type == OSType.MACOS

    def get_file_separator(self) -> str:
        """
        Get the appropriate file separator for the current OS.
        
        Returns:
            str: File separator character
        """
        return '\\' if self.is_windows() else '/'

    def normalize_path(self, path: Union[str, Path]) -> Path:
        """
        Convert a string path to a Path object and resolve any relative components.
        
        Args:
            path (Union[str, Path]): Path to normalize
            
        Returns:
            Path: Normalized path object
        """
        return Path(path).resolve()

    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """
        Check if a file exists at the specified path.
        
        Args:
            file_path (Union[str, Path]): Path to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            path = self.normalize_path(file_path)
            return path.is_file()
        except Exception as e:
            self.logger.error(f"Error checking file existence: {e}")
            return False

    def directory_exists(self, dir_path: Union[str, Path]) -> bool:
        """
        Check if a directory exists at the specified path.
        
        Args:
            dir_path (Union[str, Path]): Path to check
            
        Returns:
            bool: True if directory exists, False otherwise
        """
        try:
            path = self.normalize_path(dir_path)
            return path.is_dir()
        except Exception as e:
            self.logger.error(f"Error checking directory existence: {e}")
            return False

    def list_files(
        self,
        directory: Union[str, Path],
        pattern: str = "*",
        recursive: bool = False
    ) -> Generator[Path, None, None]:
        """
        List all files in a directory matching the given pattern.
        
        Args:
            directory (Union[str, Path]): Directory to search
            pattern (str): Glob pattern to match (default: "*")
            recursive (bool): Whether to search recursively (default: False)
            
        Yields:
            Path: Path objects for matching files
        """
        try:
            dir_path = self.normalize_path(directory)
            if recursive:
                glob_pattern = f"**/{pattern}"
            else:
                glob_pattern = pattern
                
            for file_path in dir_path.glob(glob_pattern):
                if file_path.is_file():
                    yield file_path
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return

    def create_directory(self, dir_path: Union[str, Path], exist_ok: bool = True) -> bool:
        """
        Create a directory at the specified path.
        
        Args:
            dir_path (Union[str, Path]): Path where directory should be created
            exist_ok (bool): If True, don't raise error if directory exists
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            path = self.normalize_path(dir_path)
            path.mkdir(parents=True, exist_ok=exist_ok)
            return True
        except Exception as e:
            self.logger.error(f"Error creating directory: {e}")
            return False

    def copy_file(
        self,
        source: Union[str, Path],
        destination: Union[str, Path],
        overwrite: bool = False
    ) -> bool:
        """
        Copy a file from source to destination.
        
        Args:
            source (Union[str, Path]): Source file path
            destination (Union[str, Path]): Destination file path
            overwrite (bool): Whether to overwrite existing files (default: False)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            src_path = self.normalize_path(source)
            dst_path = self.normalize_path(destination)
            
            if not src_path.is_file():
                self.logger.error("Source file does not exist")
                return False
                
            if dst_path.exists() and not overwrite:
                self.logger.error("Destination file exists and overwrite is False")
                return False
                
            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            self.logger.error(f"Error copying file: {e}")
            return False

    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file at the specified path.
        
        Args:
            file_path (Union[str, Path]): Path to file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            path = self.normalize_path(file_path)
            if path.is_file():
                path.unlink()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}")
            return False

    def get_file_info(self, file_path: Union[str, Path]) -> Optional[Dict]:
        """
        Get detailed information about a file.
        
        Args:
            file_path (Union[str, Path]): Path to file
            
        Returns:
            Optional[Dict]: Dictionary containing file information or None if error
        """
        try:
            path = self.normalize_path(file_path)
            if not path.is_file():
                return None
                
            stats = path.stat()
            return {
                'name': path.name,
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime),
                'modified': datetime.fromtimestamp(stats.st_mtime),
                'accessed': datetime.fromtimestamp(stats.st_atime),
                'extension': path.suffix,
                'parent_directory': str(path.parent)
            }
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return None

    def execute_command(
        self,
        command: Union[str, List[str]],
        shell: bool = False,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Execute a system command and return the result.
        
        Args:
            command (Union[str, List[str]]): Command to execute
            shell (bool): Whether to execute through shell (default: False)
            timeout (Optional[int]): Command timeout in seconds
            
        Returns:
            Dict: Dictionary containing return code, stdout, and stderr
        """
        try:
            if isinstance(command, str) and not shell:
                command = command.split()
                
            result = subprocess.run(
                command,
                shell=shell,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            self.logger.error("Command execution timed out")
            return {'returncode': -1, 'stdout': '', 'stderr': 'Timeout'}
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return {'returncode': -1, 'stdout': '', 'stderr': str(e)}

    def get_environment_variable(self, variable_name: str) -> Optional[str]:
        """
        Get the value of an environment variable.
        
        Args:
            variable_name (str): Name of environment variable
            
        Returns:
            Optional[str]: Value of environment variable or None if not found
        """
        try:
            return os.environ.get(variable_name)
        except Exception as e:
            self.logger.error(f"Error getting environment variable: {e}")
            return None

    def get_free_space(self, path: Union[str, Path]) -> Optional[int]:
        """
        Get free space in bytes for the drive containing the specified path.
        
        Args:
            path (Union[str, Path]): Path to check
            
        Returns:
            Optional[int]: Free space in bytes or None if error
        """
        try:
            norm_path = self.normalize_path(path)
            if self.is_windows():
                free_bytes = shutil.disk_usage(norm_path).free
            else:
                stats = os.statvfs(norm_path)
                free_bytes = stats.f_frsize * stats.f_bfree
            return free_bytes
        except Exception as e:
            self.logger.error(f"Error getting free space: {e}")
            return None
