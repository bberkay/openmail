import os
from __future__ import annotations

from consts import APP_NAME

ROOT_DIR = os.path.join(os.path.expanduser("~"), "." + APP_NAME)

class FileObject:
    def __init__(self, name: str, initial_content: any = ""):
        if "." not in name:
            raise ValueError(f"Invalid file name: {name}. File names must have a file extension.")
        if not isinstance(name, str):
            raise TypeError(f"Invalid file name: {name}. File names must be a string.")
        if not name:
            raise ValueError(f"Invalid file name: {name}. File names must not be empty.")

        self.name = name
        self._initial_content = initial_content
        self._fullpath = None

    def __repr__(self):
        return f"FileObject({self.name})"

    def create(self, fullpath: str):
        if not isinstance(fullpath, str):
            raise TypeError(f"Invalid file path: {fullpath}. File paths must be a string.")
        if not fullpath:
            raise ValueError(f"Invalid file path: {fullpath}. File paths must not be empty.")

        if os.path.exists(fullpath):
            return

        with open(fullpath, "w", encoding="utf-8") as file:
            file.write(self._initial_content)

        self._fullpath = fullpath

    def getContent(self) -> str:
        with open(self._fullpath, "r", encoding="utf-8") as file:
            content = file.read()
        return content

    def setContent(self, content: any):
        with open(self._fullpath, "w", encoding="utf-8") as file:
            file.write(content)

class DirObject:
    def __init__(self, name: str, children: list[FileObject | DirObject] = None):
        self.name = name
        self.children = children or []
        self._child_map = {child.name.split(".")[0]: child for child in self.children}
        self._fullpath = None

    def __repr__(self):
        return f"DirObject({self.name})"

    def __getitem__(self, name: str):
        """Key-based access (for example: explorer['config'])"""
        return self.get(name)

    def __getattr__(self, name: str):
        """Dot-based access (for example: explorer.config)"""
        if name in self._child_map:
            return self._child_map[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get(self, name: str):
        """Get a child by its name (used for both dot and key access)"""
        if name in self._child_map:
            return self._child_map[name]
        raise KeyError(f"'{name}' not found in {self.name}")

    def create(self, fullpath: str):
        if os.path.exists(fullpath):
            return

        os.makedirs(fullpath, exist_ok=True)
        self._fullpath = fullpath

    def display(self):
        pass

class FileSystem:
    _instance = None
    _root: DirObject

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._root = DirObject(
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

            cls._instance._create_structure(cls._instance._root)

        return cls._instance

    def _create_structure(self, obj: FileObject | DirObject, parent_path: str = ""):
        """Recursive function to create the file system structure."""
        fullpath = os.path.join(parent_path, obj.name)

        if isinstance(obj, DirObject):
            obj.create(fullpath)

            for child in obj.children:
                self._create_structure(child, fullpath)

        elif isinstance(obj, FileObject):
            obj.create(fullpath)

    @property
    def root(self) -> DirObject:
        return self._root
