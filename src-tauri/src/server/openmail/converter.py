import os
import hashlib

from openmail.types import Attachment
from openmail.encoder import FileBase64Encoder

"""
Constants
"""
MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION = 1024 # 1 KB

"""
Utility functions
"""
def get_mime_type_from_base64(base64_data: str) -> str:
    """
    Extracts the MIME type from a base64-encoded string.

    Args:
        base64_data (str): The base64-encoded string.

    Returns:
        str: The extracted MIME type.

    Example:
        >>> get_mime_type_from_base64('data:image/png;base64, iVBORw0KGgoAAAANkJggg==')
        'image/png'
    """
    if base64_data.startswith("data:"):
        return base64_data.split(";")[0].split(":")[1]
    return ""

def generate_cid_from_data(data: str, length: int = 32) -> str:
    """
    Creates a content ID from the given data.

    Args:
        data (str): The data to generate the content ID from.

    Returns:
        str: The generated content ID.
    """
    if length <= 0:
        raise ValueError("Content ID length must be greater than 0.")

    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:length]


class AttachmentConverter:
    """A static class for converting file paths, urls, etc. to `Attachment` objects."""

    @staticmethod
    def from_filepath(file_path: str) -> Attachment:
        """
        Read the given file path and convert it to an `Attachment` object.

        Args:
            file_path (str): The path to the file.

        Returns:
            Attachment: The converted `Attachment` object.

        Example:
            >>> from_filepath("/path/to/file.txt")
            Attachment(
                name="file.txt",
                size=1024,
                type="text/plain",
                path="/path/to/file.txt",
                data=None,
                cid="..."
            )
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")

        if MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION <= 0:
            raise ValueError("`MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION` must be greater than 0.")

        name, mime_type, size, content = FileBase64Encoder.read_local_file(
            file_path,
            MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION
        )
        return Attachment(
            name=name,
            size=size,
            type=mime_type,
            path=file_path,
            data=None,
            cid=generate_cid_from_data(content)
        )

    @staticmethod
    def from_url(url: str) -> Attachment:
        """
        Read the given URL and convert it to an `Attachment` object.

        Args:
            url (str): The URL of the file.

        Returns:
            Attachment: The converted `Attachment` object.

        Example:
            >>> from_url("https://example.com/file.txt")
            Attachment(
                name="file.txt",
                size=1024,
                type="text/plain",
                path="https://example.com/file.txt",
                data=None,
                cid="..."
            )
        """
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with 'http://' or 'https://'.")

        if MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION <= 0:
            raise ValueError("`MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION` must be greater than 0.")

        name, mime_type, size, content = FileBase64Encoder.read_remote_file(
            url,
            MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION
        )
        return Attachment(
            name=name,
            size=size,
            type=mime_type,
            path=url,
            data=None,
            cid=generate_cid_from_data(content)
        )

    @staticmethod
    def from_uncomplete_attachment(uncomplete_attachment: Attachment) -> Attachment:
        """
        Convert an incomplete `Attachment` object to a complete `Attachment` object.

        Args:
            uncomplete_attachment (Attachment): The incomplete `Attachment` object.

        Returns:
            Attachment: The complete `Attachment` object.

        Example:
            >>> from_uncomplete_attachment(Attachment(path="/path/to/file.txt"))
            Attachment(
                name="file.txt",
                size=1024,
                type="text/plain",
                path="/path/to/file.txt",
                data=None,
                cid="contentid123"
            )
            >>> from_uncomplete_attachment(Attachment(data="iVBORw0KGgoAAAANkJggg=="))
            Attachment(
                name=None,
                size=2048,
                type="image/png",
                path=None,
                data="iVBORw0KGgoAAAANkJggg==",
                cid="contentid123"
            )
            >>> from_uncomplete_attachment(Attachment(
            ...     name="myfile.txt",
            ...     size=None,
            ...     type=None,
            ...     path="/path/to/file.txt",
            ...     data=None,
            ...     cid=None
            ... ))
            Attachment(
                name="myfile.txt",
                size=2048,
                type="text/plain",
                path="/path/to/file.txt",
                data=None,
                cid="contentid123"
            )

        Notes:
            - Does not override existing values in the given `uncomplete_attachment` object.
        """
        if MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION <= 0:
            raise ValueError("`MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION` must be greater than 0.")

        if uncomplete_attachment.path is not None:
            name, mime_type, size, content = FileBase64Encoder.read_file(
                uncomplete_attachment.path,
                MAX_DATA_SIZE_FOR_CONTENT_ID_GENERATION
            )
            return Attachment(
                name=uncomplete_attachment.name or name,
                size=uncomplete_attachment.size or size,
                type=uncomplete_attachment.type or mime_type,
                path=uncomplete_attachment.path,
                data=uncomplete_attachment.data,
                cid=uncomplete_attachment.cid or generate_cid_from_data(content)
            )
        elif uncomplete_attachment.data is not None:
            return Attachment(
                name=uncomplete_attachment.name,
                path=uncomplete_attachment.path,
                type=uncomplete_attachment.type or get_mime_type_from_base64(uncomplete_attachment.data),
                size=uncomplete_attachment.size or len(uncomplete_attachment.data),
                data=uncomplete_attachment.data,
                cid=uncomplete_attachment.cid or generate_cid_from_data(uncomplete_attachment.data)
            )

        raise ValueError("Either `path` or `data` must be provided in the `Attachment` object.")

    @staticmethod
    def from_base64(base64_data: str) -> Attachment:
        """
        Convert a base64-encoded string to an `Attachment` object.

        Args:
            base64_data (str): The base64-encoded string.

        Returns:
            Attachment: The converted `Attachment` object.

        Example:
            >>> from_base64('data:image/png;base64, iVBORw0KGgoAAAANkJggg==')
            Attachment(
                name=None,
                size=1024,
                type='image/png',
                path=None,
                data='iVBORw0KGgoAAAANkJggg==',
                cid='contentid123'
            )
        """
        mime_type = get_mime_type_from_base64(base64_data)
        return Attachment(
            name=None,
            size=len(base64_data),
            type=mime_type,
            path=None,
            data=base64_data.replace(f"data:{mime_type};base64,", ""),
            cid=generate_cid_from_data(base64_data)
        )

    @staticmethod
    def resolve_and_convert(file_path_or_url_or_attachment: str | Attachment) -> Attachment:
        """
        Convert a file path, URL, or `Attachment` object to an `Attachment` object.

        Args:
            file_path_or_url_or_attachment (str | Attachment): The file path, URL, or `Attachment` object.

        Returns:
            Attachment: The converted `Attachment` object.

        Example:
            >>> resolve_and_convert("/path/to/file.txt")
            Attachment(
                name="file.txt",
                size=1024,
                type="text/plain",
                path="/path/to/file.txt",
                data=None,
                cid="contentid123"
            )
            >>> resolve_and_convert("https://example.com/file.txt")
            Attachment(
                name="file.txt",
                size=1024,
                type="text/plain",
                path="https://example.com/file.txt",
                data=None,
                cid="contentid123"
            )
            >>> resolve_and_convert(Attachment(path="/path/to/file.txt"))
            Attachment(
                name="file.txt",
                size=1024,
                type="text/plain",
                path="/path/to/file.txt",
                data=None,
                cid="contentid123"
            )
        """
        if isinstance(file_path_or_url_or_attachment, Attachment):
            return AttachmentConverter.from_uncomplete_attachment(
                file_path_or_url_or_attachment
            )
        elif file_path_or_url_or_attachment.startswith(("http://", "https://")):
            return AttachmentConverter.from_url(
                file_path_or_url_or_attachment
            )
        elif file_path_or_url_or_attachment.startswith("data:"):
            return AttachmentConverter.from_base64(
                file_path_or_url_or_attachment
            )
        else:
            return AttachmentConverter.from_filepath(
                file_path_or_url_or_attachment
            )
