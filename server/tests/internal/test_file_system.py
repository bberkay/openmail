import unittest
import os
import shutil
from pathlib import Path

from src.internal.file_system import Root, DirObject, FileObject

# TODO: Read lines, write lines, read and write tests should be written
class TestFileSystem(unittest.TestCase):
    def setUp(self):
        print("Setting up test `TestFileSystem`...")
        self._test_root_name = "test_file_system"
        self._test_root_fullpath = os.path.join(".", self._test_root_name)
        self._test_root = Root(self._test_root_name, ".")
        assert os.path.exists(self._test_root_fullpath)

    def get_complex_file_structure(self) -> list[str]:
        """
        test-file-system/
        ├── a/
        │   ├── a-1/
        │   │   ├── a-1-1/
        │   │   │   └── a-1-1-1.txt
        │   │   └── a-1-2/
        │   └── a-2/
        │       └── a-2-1/
        └── b/
            ├── b-1/
            │   ├── b-1-1/
            │   │   ├── b-1-1-1.txt
            │   │   └── b-1-1-2.txt
            │   ├── b-1-2/
            │   │   ├── b-1-2-1.txt
            │   │   └── b-1-2-2.txt
            │   └── b-1-3.txt
            ├── b-2/
            │   └── b-2-1/
            │       └── b-2-1-1.txt
            └── b-3.txt
        """
        structure = [
            "a/a-1/a-1-1/a-1-1-1.txt",
            "a/a-1/a-1-2/",
            "a/a-2/a-2-1/",
            "b/b-1/b-1-1/b-1-1-1.txt",
            "b/b-1/b-1-1/b-1-1-2.txt",
            "b/b-1/b-1-2/b-1-2-1.txt",
            "b/b-1/b-1-2/b-1-2-2.txt",
            "b/b-1/b-1-3.txt",
            "b/b-2/b-2-1/b-2-1-1.txt",
            "b/b-3.txt",
        ]

        # Format structure
        for item in structure:
            if item.endswith("/"):
                item = item[:-1]

        return structure

    def test_create_simple_dir_under_root(self):
        print("test_create_simple_dir_under_root...")
        dir_name = "hello"
        self._test_root.append(DirObject(dir_name))
        self.assertTrue(os.path.exists(dir_name))

    def test_create_simple_file_under_root(self):
        print("test_create_simple_file_under_root...")
        file_name = "hello.txt"
        self._test_root.append(FileObject(file_name))
        self.assertTrue(os.path.exists(os.path.join(self._test_root_fullpath, file_name)))

    def test_create_simple_dir_under_dir_object(self):
        print("test_create_simple_dir_under_dir_object...")
        dir_name = "hello"
        dir = DirObject(dir_name)
        self._test_root.append(dir)
        sub_dir_name = "random-subfolder"
        sub_dir_path = os.path.join(dir.fullpath, sub_dir_name)
        sub_dir = DirObject(sub_dir_name)
        dir.append(sub_dir)
        self.assertTrue(os.path.exists(sub_dir_path))

    def test_create_simple_file_under_dir_object(self):
        print("test_create_simple_file_under_dir_object...")
        dir_name = "hello"
        dir = DirObject(dir_name)
        self._test_root.append(dir)
        sub_file_name = "random-subfile.txt"
        sub_file_path = os.path.join(dir.fullpath, sub_file_name)
        sub_file = FileObject(sub_file_name)
        dir.append(sub_file)
        self.assertTrue(os.path.exists(sub_file_path))

    def test_create_folder_overwrite_true_under_root(self):
        print("test_create_folder_overwrite_true_under_root...")
        dir_name = "hello"
        fullpath = os.path.join(self._test_root_fullpath, dir_name)
        os.makedirs(fullpath)
        self.assertTrue(os.path.exists(fullpath))

        random_subfolder_name = "random-subfolder"
        random_subfolder_path = os.path.join(fullpath, random_subfolder_name)
        os.makedirs(random_subfolder_path)
        self.assertTrue(os.path.exists(random_subfolder_path))

        self._test_root.append(DirObject(dir_name), overwrite=True)
        self.assertTrue(os.path.exists(fullpath))
        self.assertFalse(os.path.exists(random_subfolder_path))

    def test_create_folder_overwrite_false_under_root(self):
        print("test_create_folder_overwrite_false_under_root...")
        dir_name = "hello"
        fullpath = os.path.join(self._test_root_fullpath, dir_name)
        os.makedirs(fullpath)
        self.assertTrue(os.path.exists(fullpath))

        random_subfolder_name = "random-subfolder"
        random_subfolder_path = os.path.join(fullpath, random_subfolder_name)
        os.makedirs(random_subfolder_path)
        self.assertTrue(os.path.exists(random_subfolder_path))

        self._test_root.append(DirObject(dir_name))
        self.assertTrue(os.path.exists(fullpath))
        self.assertTrue(os.path.exists(random_subfolder_path))

    def test_create_file_overwrite_true_under_root(self):
        print("test_create_file_overwrite_true_under_root...")
        file_name = "hello.txt"
        fullpath = os.path.join(self._test_root_fullpath, file_name)
        Path(fullpath).touch()
        self.assertTrue(os.path.exists(fullpath))

        with open(fullpath, "w") as f:
            f.write("Hello, world!")

        self._test_root.append(FileObject(file_name), overwrite=True)
        self.assertTrue(os.path.exists(fullpath))
        with open(fullpath, "r") as f:
            content = f.read()
        self.assertFalse(content)

    def test_create_file_overwrite_false_under_root(self):
        print("test_create_file_overwrite_false_under_root...")
        file_name = "hello.txt"
        fullpath = os.path.join(self._test_root_fullpath, file_name)
        Path(fullpath).touch()
        self.assertTrue(os.path.exists(fullpath))

        writed_content = "Hello, world!"
        with open(fullpath, "w") as f:
            f.write(writed_content)

        self._test_root.append(FileObject(file_name))
        self.assertTrue(os.path.exists(fullpath))
        with open(fullpath, "r") as f:
            read_content = f.read()
        self.assertEqual(writed_content, read_content)

    def test_write_file_under_root(self):
        print("test_write_file_under_root...")
        file_name = "hello.txt"
        file = FileObject(file_name)
        self._test_root.append(file)

        writed_content = "Hello, world!"
        file.write(writed_content)

        fullpath = os.path.join(self._test_root_fullpath, file.name)
        with open(fullpath, "r") as f:
            read_content = f.read()
        self.assertEqual(writed_content, read_content)

    def test_read_file_under_root(self):
        print("test_read_file_under_root...")
        file_name = "hello.txt"
        file = FileObject(file_name)
        self._test_root.append(file)

        writed_content = "Hello, world!"
        file.write(writed_content)

        fullpath = os.path.join(self._test_root_fullpath, file.name)
        with open(fullpath, "r") as f:
            read_content = f.read()

        self.assertEqual(writed_content, read_content)
        self.assertEqual(read_content, file.read())

    def test_create_complex_file_structure_under_root(self):
        print("test_create_complex_structure_under_root...")
        structure = self.get_complex_file_structure()

        for item in structure:
            if item.endswith(".txt"):
                dir_path, file_path = item.rsplit("/", 1)
                dir = DirObject(dir_path)
                self._test_root.append(dir)
                dir.append(FileObject(file_path))
            else:
                path = os.path.join(*item.split("/"))
                self._test_root.append(DirObject(path))

            self.assertTrue(os.path.exists(os.path.join(self._test_root.fullpath, item)))

    def test_traverse_folder_under_root(self):
        print("test_traverse_folder_under_root...")
        structure = self.get_complex_file_structure()

        print("Creating complex file structure manually...")
        root = Path(self._test_root_fullpath)
        for item in structure:
            path = root / item
            if item.endswith(".txt"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch(exist_ok=True)
            else:
                path.mkdir(parents=True, exist_ok=True)

            self.assertTrue(os.path.exists(path))

        print("Traversing...")
        base_dirs = {item.split("/", 1)[0] for item in structure}
        for base_dir in base_dirs:
            self._test_root.append(DirObject(base_dir))

        self._test_root.display()

        nodes_manually_listed = []
        def walk(dir_path: Path):
            for item in Path(dir_path).iterdir():
                nodes_manually_listed.append(str(item))
                if item.is_dir():
                    walk(item)

        walk(Path(self._test_root.fullpath))

        self.assertCountEqual(
            [node[node.find(self._test_root.name):] for node in self._test_root.nodes()],
            [node[node.find(self._test_root.name):] for node in nodes_manually_listed]
        )

    def tearDown(self):
        print("Cleaning up test `TestFileSystem`...")
        shutil.rmtree(self._test_root_fullpath)
