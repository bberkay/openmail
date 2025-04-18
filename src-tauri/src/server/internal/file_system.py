from __future__ import annotations
import os
from typing import Any, cast

from consts import APP_NAME

class FileObject:
    def __init__(self, name: str, initial_content: Any = ""):
        if "." not in name:
            raise ValueError(f"Invalid file name: {name}. File names must have a file extension.")
        if not isinstance(name, str):
            raise TypeError(f"Invalid file name: {name}. File names must be a string.")
        if not name:
            raise ValueError(f"Invalid file name: {name}. File names must not be empty.")

        self._name = name
        self._initial_content = initial_content
        self._fullpath: str = ""

    def __repr__(self):
        return f"FileObject({self._name})"

    def __call__(self):
        return self

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self) -> None:
        raise AttributeError("Modification of 'name' is not allowed.")

    @property
    def fullpath(self) -> str:
        if not self._fullpath:
            raise FileNotFoundError
        return self._fullpath

    @fullpath.setter
    def fullpath(self) -> None:
        raise AttributeError("Modification of 'fullpath' is not allowed.")

    def create(self, fullpath: str, overwrite: bool = False) -> None:
        if not isinstance(fullpath, str):
            raise TypeError(f"Invalid file path: {fullpath}. File paths must be a string.")
        if not fullpath:
            raise ValueError(f"Invalid file path: {fullpath}. File paths must not be empty.")

        self._fullpath = fullpath

        if not overwrite and os.path.exists(self.fullpath):
            return

        with open(self.fullpath, "w", encoding="utf-8") as f:
            f.write(self._initial_content)

    def read(self) -> str:
        with open(self.fullpath, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def write(self, content: Any) -> None:
        with open(self.fullpath, "w", encoding="utf-8") as f:
            f.write(content)

    def clear(self) -> None:
        with open(self.fullpath, "w", encoding="utf-8") as f:
            f.write("")

class DirObject:
    def __init__(self, name: str, children: list[FileObject | DirObject] | None = None):
        self.name = name
        self._children = children or []
        self._fullpath: str = ""

    def __repr__(self):
        return f"DirObject({self.name})"

    def __getitem__(self, name: str) -> DirObject | FileObject:
        """Key-based access (for example: explorer['config'])"""
        return self.get(name)

    def __setitem__(self, key, value):
        """Prevent overwriting __getitem__"""
        raise AttributeError(f"Modification of '{key}' via __setitem__ is not allowed.")

    @property
    def fullpath(self) -> str:
        if not self._fullpath:
            raise FileNotFoundError
        return self._fullpath

    @fullpath.setter
    def fullpath(self) -> None:
        raise AttributeError("Modification of 'fullpath' is not allowed.")

    @property
    def children(self) -> list[FileObject | DirObject]:
        return self._children

    @children.setter
    def children(self) -> None:
        raise AttributeError("Modification of 'children' is not allowed.")

    def get(self, name: str) -> DirObject | FileObject:
        """Get a child by its name (used for both dot and key access)"""
        for child in self._children:
            if child.name == name:
                return child
        raise KeyError(f"'{name}' not found in {self.name}")

    def create(self, fullpath: str, overwrite: bool = False) -> None:
        if not isinstance(fullpath, str):
            raise TypeError(f"Invalid directory path: {fullpath}. Directory paths must be a string.")
        if not fullpath:
            raise ValueError(f"Invalid directory path: {fullpath}. Directory paths must not be empty.")

        self._fullpath = fullpath

        if not overwrite and os.path.exists(self.fullpath):
            return

        os.makedirs(self.fullpath, exist_ok=True)

    def display(self, indent: int = 0) -> None:
        """Recursively display the directory structure as a tree."""
        prefix = " " * (indent * 4) + ("└── " if indent > 0 else "")
        print(f"{prefix}{self.name}/")

        for child in self._children:
            if isinstance(child, DirObject):
                child.display(indent + 1)
            elif isinstance(child, FileObject):
                file_prefix = " " * ((indent + 1) * 4) + "└── "
                print(f"{file_prefix}{child.name}")

"""
Constants
"""
ROOT_DIR = os.path.join(os.path.expanduser("~"), "." + APP_NAME)
BASE_STRUCTURE = DirObject(
    ROOT_DIR,
    [
        FileObject("uvicorn.info"),
        FileObject("preferences.json"),
        DirObject(
            "logs",
            [
                FileObject("uvicorn.log"),
            ],
        )
    ],
)

class FileSystem:
    _instance = None
    _root = BASE_STRUCTURE

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._create_structure(cls._root)

        return cls._instance

    def _create_structure(self,
        obj: FileObject | DirObject,
        parent_path: str = "",
        remove_exist: bool = False
    ) -> None:
        fullpath = os.path.join(parent_path, obj.name)

        if isinstance(obj, DirObject):
            obj.create(fullpath, overwrite=remove_exist)

            for child in obj.children:
                self._create_structure(child, fullpath)

        elif isinstance(obj, FileObject):
            obj.create(fullpath, overwrite=remove_exist)

    @property
    def root(self) -> DirObject:
        if not self._root:
            raise Exception("FileSystem has not been initialized yet.")

        return self._root

    @root.setter
    def root(self, value) -> None:
        raise AttributeError("Modification of 'root' is not allowed.")

    def reset(self) -> None:
        # In the `uvicorn.info` file we store the current URL and PID
        # so that we can get the server's URL from tha tauri app
        # and also can kill the server completely. So get the current
        # URL and PID from the `uvicorn.info` file and write them back
        # as initial content.
        current_uvicorn_info = self.get_uvicorn_info().read()
        self._root = BASE_STRUCTURE
        self._create_structure(self._root, remove_exist=True)
        cast(FileObject, self.root["uvicorn.info"]).write(current_uvicorn_info)


    # Base FileObject/DirObject methods.

    def get_uvicorn_info(self) -> FileObject:
        return cast(FileObject, self._root["uvicorn.info"])

    def get_uvicorn_log(self) -> FileObject:
        return cast(FileObject, cast(DirObject, self._root["logs"])["uvicorn.log"])

    def get_preferences(self) -> FileObject:
        return cast(FileObject, self._root["preferences.json"])
