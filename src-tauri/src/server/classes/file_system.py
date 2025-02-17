from __future__ import annotations
import os
from typing import Any

from consts import APP_NAME

ROOT_DIR = os.path.join(os.path.expanduser("~"), "." + APP_NAME)

class FileObject:
    def __init__(self, name: str, initial_content: Any = ""):
        if "." not in name:
            raise ValueError(f"Invalid file name: {name}. File names must have a file extension.")
        if not isinstance(name, str):
            raise TypeError(f"Invalid file name: {name}. File names must be a string.")
        if not name:
            raise ValueError(f"Invalid file name: {name}. File names must not be empty.")

        self.name = name
        self._initial_content = initial_content
        self.fullpath = None

    def __repr__(self):
        return f"FileObject({self.name})"

    def __call__(self):
        return self

    def create(self, fullpath: str, overwrite: bool = False):
        if not isinstance(fullpath, str):
            raise TypeError(f"Invalid file path: {fullpath}. File paths must be a string.")
        if not fullpath:
            raise ValueError(f"Invalid file path: {fullpath}. File paths must not be empty.")

        self.fullpath = fullpath

        if not overwrite and os.path.exists(self.fullpath):
            return

        with open(self.fullpath, "w", encoding="utf-8") as file:
            file.write(self._initial_content)

    def read(self) -> str:
        if not self.fullpath:
            raise FileNotFoundError

        with open(self.fullpath, "r", encoding="utf-8") as file:
            content = file.read()
        return content

    def write(self, content: Any):
        if not self.fullpath:
            raise FileNotFoundError

        with open(self.fullpath, "w", encoding="utf-8") as file:
            file.write(content)

    def clear(self):
        if not self.fullpath:
            raise FileNotFoundError

        with open(self.fullpath, "w", encoding="utf-8") as file:
            file.write("")

class DirObject:
    def __init__(self, name: str, children: list[FileObject | DirObject] | None = None):
        self.name = name
        self.children = children or []
        self.fullpath = None

    def __repr__(self):
        return f"DirObject({self.name})"

    def __getitem__(self, name: str) -> DirObject | FileObject:
        """Key-based access (for example: explorer['config'])"""
        return self.get(name)

    def __getattr__(self, name: str) -> DirObject | FileObject:
        """Dot-based access (for example: explorer.config)"""
        for child in self.children:
            if child.name.split(".")[0] == name:
                return child
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get(self, name: str) -> DirObject | FileObject:
        """Get a child by its name (used for both dot and key access)"""
        for child in self.children:
            if child.name == name:
                return child
        raise KeyError(f"'{name}' not found in {self.name}")

    def create(self, fullpath: str, overwrite: bool = False):
        if not isinstance(fullpath, str):
            raise TypeError(f"Invalid directory path: {fullpath}. Directory paths must be a string.")
        if not fullpath:
            raise ValueError(f"Invalid directory path: {fullpath}. Directory paths must not be empty.")

        self.fullpath = fullpath

        if not overwrite and os.path.exists(self.fullpath):
            return

        os.makedirs(self.fullpath, exist_ok=True)

    def display(self, indent: int = 0):
        """Recursively display the directory structure as a tree."""
        prefix = " " * (indent * 4) + ("└── " if indent > 0 else "")
        print(f"{prefix}{self.name}/")

        for child in self.children:
            if isinstance(child, DirObject):
                child.display(indent + 1)
            elif isinstance(child, FileObject):
                file_prefix = " " * ((indent + 1) * 4) + "└── "
                print(f"{file_prefix}{child.name}")

class FileSystem:
    _instance = None
    _root = DirObject(
        ROOT_DIR,
        [
            FileObject("uvicorn.info"),
            DirObject(
                "logs",
                [
                    FileObject("uvicorn.log"),
                ],
            )
        ],
    )

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._create_structure(cls._instance._root)

        return cls._instance

    def _create_structure(self, obj: FileObject | DirObject, parent_path: str = "", remove_exist: bool = False):
        """Recursive function to create the file system structure."""
        fullpath = os.path.join(parent_path, obj.name)

        if isinstance(obj, DirObject):
            obj.create(fullpath, overwrite=remove_exist)

            for child in obj.children:
                self._create_structure(child, fullpath)

        elif isinstance(obj, FileObject):
            obj.create(fullpath, overwrite=remove_exist)

    @property
    def root(self) -> DirObject:
        return self._root

    def reset(self):
        # In the `uvicorn.info` file we store the current URL and PID
        # so that we can get the server's URL from tha tauri app
        # and also can kill the server completely. So get the current
        # URL and PID from the `uvicorn.info` file and write them back
        # as initial content.
        self._root = DirObject(
            ROOT_DIR,
            [
                FileObject("uvicorn.info", self._root["uvicorn.info"].read()),
                DirObject(
                    "logs",
                    [
                        FileObject("uvicorn.log"),
                    ],
                )
            ],
        )
        self._create_structure(self._root, remove_exist=True)
