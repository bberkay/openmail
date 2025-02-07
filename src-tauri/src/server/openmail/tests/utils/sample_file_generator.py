import random
import os
import base64
import mimetypes
from abc import ABC, abstractmethod

"""
Constants
"""
IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "tiff", "ico", "raw", "heic", "heif", "apng", "avif"]
MIMETYPE_GUESS_FAILBACK = "application/octet-stream"

class SampleFileGenerator(ABC):
    @abstractmethod
    def as_filepath(self, count:int = 1, all_different: bool = False) -> list[str]:
        pass

    @abstractmethod
    def as_url(self, count:int = 1, all_different: bool = False) -> list[str]:
        pass

    @abstractmethod
    def as_base64(self, count:int = 1, all_different: bool = False) -> list[str]:
        pass

class FileGenerator:
    """Class for generating sample files."""

    @staticmethod
    def as_filepath(
        media_type: str,
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate sample files from a folder.

        Args:
            media_type (str): The media type of the files to generate.
            count (int, optional): The number of files to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique files.
            Defaults to False.

        Returns:
            list[str]: A list of file paths.

        Example:
            >>> SampleFileGenerator.as_filepath(
            ...    "images",
            ...    count=3,
            ...    all_different=True
            ... )
            [
                '/path/to/image1.jpg',
                '/path/to/image2.jpg',
                '/path/to/image3.jpg'
            ]
        """
        folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"media/{media_type}")
        children = os.listdir(folder_path)

        if len(children) == 0:
            return []

        choices = []
        while len(choices) < count:
            random_child = random.choice(children)
            if not all_different or random_child not in choices:
                choices.append(os.path.join(folder_path, random_child))

        return choices if len(choices) > 1 else choices[0]

    @staticmethod
    def as_url(
        ext_type: str | list[str] | None = None,
        count: int = 1,
        all_different: bool = False,
        excluded_ext_type: str | list[str] | None = None
    ) -> list[str]:
        """
        Generate sample files from URLs.

        Args:
            ext_type (str | list[str] | None, optional): The file extensions to filter by. Defaults to None.
            count (int, optional): The number of files to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique files. Defaults to False.
            excluded_ext_type (str | list[str] | None, optional): The file extensions to exclude. Defaults to None.

        Returns:
            list[str]: A list of file URLs.

        Example:
            >>> SampleFileGenerator.as_url(
            ...    ext_type=["jpg", "jpeg"],
            ...    count=3,
            ...    all_different=True
            ... )
            [
                'https://example.com/image1.jpg',
                'https://example.com/image2.jpg',
                'https://example.com/image3.jpg'
            ]
            >>> SampleFileGenerator.as_url(
            ...    ext_type=["jpg", "jpeg"],
            ...    count=3,
            ...    all_different=True,
            ...    excluded_ext_type=["png"]
            ... )
            [
                'https://example.com/image1.jpg',
                'https://example.com/image2.jpg',
                'https://example.com/image3.jpeg'
            ]
        """
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"media/urls.txt")
        filtered_urls = []
        with open(file_path, "r") as f:
            urls = f.readlines()
            for url in urls:
                url = url.strip().replace("\n", "")
                if not ext_type and not excluded_ext_type:
                    filtered_urls.append(url)
                    continue

                url_ext = url.split(".")[-1].strip()
                if ext_type and url_ext in ext_type:
                    filtered_urls.append(url)
                if excluded_ext_type and url_ext in excluded_ext_type:
                    filtered_urls.remove(url)

        choices = []
        while len(choices) < count:
            random_line = random.choice(filtered_urls)
            if not all_different or random_line not in choices:
                choices.append(random_line)

        return choices if len(choices) > 1 else choices[0]

    @staticmethod
    def as_base64(files: str | list[str]) -> list[str]:
        """
        Convert sample files to base64-encoded strings.

        Args:
            files (str | list[str]): The file paths or URLs to convert.

        Returns:
            list[str]: A list of base64-encoded strings.

        Example:
            >>> SampleFileGenerator.as_base64([
            ...    "/path/to/file1.txt",
            ...    "/path/to/file2.txt"
            ... ])
            [
                "data:text/plain;base64,SGVsbG8sIHdvcmxkIQ==",
                "data:text/plain;base64,SGVsbG8sIHdvcmxkIQ=="
            ]
        """
        def create_base64_header(file_path: str) -> str:
            """Creates a base64 header for a given file path."""
            return "data:" + (mimetypes.guess_type(file_path)[0] or MIMETYPE_GUESS_FAILBACK) + ";base64,"

        if isinstance(files, str):
            files = [files]

        base64_strings = []
        for file_path in files:
            with open(file_path, "rb") as f:
                base64_strings.append(
                    create_base64_header(file_path) + base64.b64encode(f.read()).decode("utf-8")
                )

        return base64_strings

class SampleImageGenerator(SampleFileGenerator):
    """Generates sample images."""

    def __init__(self) -> None:
        super().__init__()

    def as_filepath(self, count: int = 1, all_different: bool = False) -> list[str]:
        """
        Generate sample images from a folder.

        Args:
            count (int, optional): The number of images to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique images. Defaults to False.

        Returns:
            list[str] | str: A list of image file paths.

        Example:
            >>> SampleImageGenerator.as_filepath(
            ...    count=3,
            ...    all_different=True
            ... )
            [
                '/path/to/image1.jpg',
                '/path/to/image2.jpg',
                '/path/to/image3.jpg'
            ]
        """
        return FileGenerator().as_filepath("images", count, all_different)

    def as_url(self, count: int = 1, all_different: bool = False) -> list[str]:
        """
        Generate sample images from URLs.

        Args:
            count (int, optional): The number of images to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique images. Defaults to False.

        Returns:
            list[str] | str: A list of image URLs.

        Example:
            >>> SampleImageGenerator.as_url(
            ...    count=3,
            ...    all_different=True
            ... )
            [
                'https://example.com/image1.jpg',
                'https://example.com/image2.jpg',
                'https://example.com/image3.jpg'
            ]
        """
        return FileGenerator().as_url(IMAGE_EXTENSIONS, count, all_different)

    def as_base64(self, count: int = 1, all_different: bool = False) -> list[str]:
        """
        Convert sample images to base64-encoded strings.

        Args:
            count (int, optional): The number of images to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique images. Defaults to False.

        Returns:
            list[str]: A list of base64-encoded strings.

        Example:
            >>> SampleImageGenerator.as_base64(
            ...    count=3,
            ...    all_different=True
            ... )
            [
                'data:image/jpeg;base64,SGVsbG8sIHdvcmxkIQ==',
                'data:image/jpeg;base64,SGVsbG8sIHdvcmxkIQ==',
                'data:image/jpeg;base64,SGVsbG8sIHdvcmxkIQ=='
            ]
        """
        return FileGenerator().as_base64(SampleImageGenerator().as_filepath(count, all_different))


class SampleDocumentGenerator(SampleFileGenerator):
    """Generates sample documents."""

    def as_filepath(self, count: int = 1, all_different: bool = False) -> list[str]:
        """
        Generate sample documents from a folder.

        Args:
            count (int, optional): The number of documents to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique documents. Defaults to False.

        Returns:
            list[str]: A list of document file paths.

        Example:
            >>> SampleDocumentGenerator.as_filepath(
            ...    count=3,
            ...    all_different=True
            ... )
            [
                '/path/to/document1.docx',
                '/path/to/document2.docx',
                '/path/to/document3.docx'
            ]
        """
        return FileGenerator().as_filepath("docs", count, all_different)

    def as_url(self, count: int = 1, all_different: bool = False) -> list[str]:
        """
        Generate sample documents from URLs.

        Args:
            count (int, optional): The number of documents to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique documents. Defaults to False.

        Returns:
            list[str]: A list of document URLs.

        Example:
            >>> SampleDocumentGenerator.as_url(
            ...    count=3,
            ...    all_different=True
            ... )
            [
                'https://example.com/document1.docx',
                'https://example.com/document2.docx',
                'https://example.com/document3.docx'
            ]
        """
        return FileGenerator().as_url(None, count, all_different, excluded_ext_type=IMAGE_EXTENSIONS)


class SampleVideoGenerator(SampleFileGenerator):
    """Generates sample videos."""

    def as_filepath(self, count: int = 1, all_different: bool = False) -> list[str]:
        """
        Generate sample videos from a folder.

        Args:
            count (int, optional): The number of videos to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique videos. Defaults to False.

        Returns:
            list[str]: A list of video file paths.

        Example:
            >>> SampleVideoGenerator().as_filepath(
            ...    count=3,
            ...    all_different=True
            ... )
            [
                '/path/to/video1.mp4',
                '/path/to/video2.mp4',
                '/path/to/video3.mp4',
            ]
        """
        return FileGenerator().as_filepath("videos", count, all_different)

    def as_url(self, count: int = 1, all_different: bool = False) -> list[str]:
        """
        Generate sample videos from URLs.

        Args:
            count (int, optional): The number of videos to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique videos. Defaults to False.

        Returns:
            list[str]: A list of video URLs.

        Example:
            >>> SampleVideoGenerator().as_url(
            ...    count=3,
            ...    all_different=True
            ... )
            [
                'https://example.com/video1.mp4',
                'https://example.com/video2.mp4',
                'https://example.com/video3.mp4',
            ]
        """
        return FileGenerator().as_url(None, count, all_different, excluded_ext_type=IMAGE_EXTENSIONS)
