from __future__ import annotations
import os
import shutil
from pathlib import Path

from typing import TypeVar, Union

from src.consts import APP_NAME

T = TypeVar("T", bound=Union["DirObject", "FileObject"])

"""
Constants
"""
if not APP_NAME:
    raise Exception("To create file system, app name must be provided")

ROOT_DIR = os.path.join(os.path.expanduser("~"), "." + APP_NAME.lower())

class FileObject:
    def __init__(self, name: str):
        if not name:
            raise ValueError(f"Invalid file name: {name}. File names must not be empty.")

        self._name = name
        self._fullpath: str = ""

    @property
    def name(self):
        return self._name

    @property
    def fullpath(self):
        return self._fullpath

    def _create(self, overwrite: bool = False) -> FileObject:
        """Create the file on disk, optionally overwriting it."""
        if os.path.exists(self.fullpath):
            if not overwrite:
                return self
            else:
                os.remove(self.fullpath)

        Path(self.fullpath).touch()
        return self

    def read(self, chunk_size: int | None = None, strip: bool = False) -> str:
        """Read and return the file content as a string."""
        if not os.path.exists(self.fullpath):
            raise FileNotFoundError(f"Cannot read: file does not exist -> {self.fullpath}")

        if chunk_size is None:
            with open(self.fullpath, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            # Stream in chunks for large files
            chunks = []
            with open(self.fullpath, "r", encoding="utf-8") as f:
                while chunk := f.read(chunk_size):
                    chunks.append(chunk)
            content = "".join(chunks)

        return content.strip() if strip else content

    def readlines(self, start_at_line: int = 1, stop_at_line: int = -1) -> list[str]:
        """Reads lines from a file, optionally between specific line numbers."""
        lines = []
        with open(self.fullpath, 'r', encoding='utf-8') as f:
            current_line = 0
            while line := f.readline():
                current_line += 1
                if current_line < start_at_line:
                    continue
                if stop_at_line != -1 and current_line > stop_at_line:
                    break
                lines.append(line.rstrip('\n'))
        return lines

    def write(self, content: str, overwrite: bool = False, newline: bool = True) -> None:
        """Write text to the file"""
        mode = "w" if overwrite else "a"
        with open(self.fullpath, mode, encoding="utf-8") as f:
            f.write(content + ("\n" if newline else ""))

    def writelines(self, lines: list[str], newline: bool = True, overwrite: bool = False) -> None:
        """Write multiple lines to the file"""
        mode = "w" if overwrite else "a"
        with open(self.fullpath, mode, encoding="utf-8") as f:
            for line in lines:
                f.write(line + ("\n" if newline else ""))

class DirObject:
    def __init__(self, name: str):
        self._name = name
        self._children: list[DirObject | FileObject] = []
        self._fullpath: str = ""

    @property
    def name(self):
        return self._name

    @property
    def fullpath(self):
        return self._fullpath

    @property
    def children(self):
        return self._children

    def __repr__(self):
        return f"DirObject({self.name})"

    def __getitem__(self, name: str) -> DirObject | FileObject:
        """Key-based access (for example: explorer['config'])"""
        return self.get(name)

    def __setitem__(self, key, value):
        """Prevent overwriting __getitem__"""
        raise AttributeError(f"Modification of '{key}' via __setitem__ is not allowed.")

    def get(self, name: str) -> DirObject | FileObject:
        """Get a child by its name (used for both dot and key access)"""
        for child in self.children:
            if child.name == name:
                return child
        raise KeyError(f"'{name}' not found in {self.name}")

    def _traverse(self, dir: DirObject):
        """Populate children list by scanning the directory on disk."""
        dir_path = Path(dir.fullpath)
        for item in dir_path.iterdir():
            dir.append(DirObject(item.name) if item.is_dir() else FileObject(item.name))

    def _create(self, overwrite: bool = False) -> DirObject:
        """Create the directory on disk, optionally overwriting existing content."""
        if os.path.exists(self.fullpath):
            if overwrite:
               shutil.rmtree(self.fullpath)
            else:
                self._traverse(self)
                return self

        os.makedirs(self.fullpath, exist_ok=True)
        return self

    def append[T](self, child: T, overwrite: bool = False) -> T:
        """Add a child directory or file, creating it on disk."""
        if not isinstance(child, DirObject) and not isinstance(child, FileObject):
            raise TypeError("Invalid child type. Child must be DirObject or FileObject")

        child._fullpath = os.path.join(self.fullpath, child.name) # type: ignore[reportAttributeAccessIssue]
        self.children.append(child._create(overwrite))
        return child

    def display(self, indent: int = 0) -> None:
        """Recursively display the directory structure as a tree."""
        prefix = " " * (indent * 4) + ("└── " if indent > 0 else "")
        print(f"{prefix}{self.name}/")

        for child in self.children:
            if isinstance(child, DirObject):
                child.display(indent + 1)
            elif isinstance(child, FileObject):
                file_prefix = " " * ((indent + 1) * 4) + "└── "
                print(f"{file_prefix}{child.name}")

    def nodes(self) -> list[str]:
        """Return a flat list of full paths of all children recursively."""
        node_list = []

        def walk(children):
            for child in children:
                node_list.append(child.fullpath)
                if isinstance(child, DirObject):
                    walk(child.children)

        walk(self.children)
        return node_list

class Root(DirObject):
    def __init__(self, name: str, parent: str = ROOT_DIR):
        """Initialize root directory at the specified parent path."""
        super().__init__(name)
        self._fullpath = os.path.join(parent, name) # type: ignore[reportAttributeAccessIssue]
        self._create()

__all__ = [
    "Root",
    "DirObject",
    "FileObject"
]
