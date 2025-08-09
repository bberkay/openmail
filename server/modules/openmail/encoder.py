import os
import base64
import mimetypes
import urllib.request
from typing import Generator

"""
Constants
"""
DEFAULT_FALLBACK_MIMETYPE = 'application/octet-stream'
DEFAULT_RETRY_READ_LIMIT = 3

"""
Utility Functions
"""
def calculate_chunk_size(total_size_in_bytes: int) -> int:
    """
    Calculate the chunk size based on the total size.

    Args:
        total_size_in_bytes (int): Total size in bytes of the data

    Returns:
        int: The calculated chunk size

    Example:
        >>> calculate_chunk_size(10 * 1024 * 1024) # 10 MB
        512 * 1024 # 512 KB
        >>> calculate_chunk_size(100 * 1024 * 1024) # 100 MB
        4 * 1024 * 1024 # 4 MB
        >>> calculate_chunk_size(50 * 1024 * 1024) # 50 MB
        2 * 1024 * 1024 # 2 MB
    """
    min_chunk = 512 * 1024  # 512 KB
    max_chunk = 4 * 1024 * 1024  # 4 MB
    threshold_small = 10 * 1024 * 1024  # 10 MB
    threshold_large = 100 * 1024 * 1024  # 100 MB

    if total_size_in_bytes <= threshold_small:
        return min_chunk
    elif total_size_in_bytes >= threshold_large:
        return max_chunk
    else:
        scale = (total_size_in_bytes - threshold_small) / (threshold_large - threshold_small)
        return int(min_chunk + scale * (max_chunk - min_chunk))

class FileBase64Encoder:
    """A static class for reading and encoding files to base64-encoded strings."""

    @staticmethod
    def read_remote_file(
        file_path: str,
        fetch_size: int = None
    ) -> tuple[str, str, int, str]:
        """
        Fetches the content of a remote file and returns it as a mime type,
        base64-encoded string, with an optional fetch size limit.

        Args:
            file_path (str): The URL of the remote file.
            fetch_size (int, optional): The maximum size to fetch from the file, in bytes.

        Returns:
            tuple: Mime type, base64-encoded string, and size of the file content.

        Example:
            >>> read_remote_file("https://example.com/file.txt", fetch_size=1024)
            ("file.txt", "text/plain", 2048, "SGVsbG8sIHdvcmxkIQ==")
        """
        if fetch_size and fetch_size <= 0:
            raise ValueError("`fetch_size` must be greater than 0 if provided.")

        with urllib.request.urlopen(file_path) as response:
            chunks = []
            total_fetched = 0
            retry_count = 1
            size = int(response.headers.get("Content-Length", total_fetched))
            chunk_size = calculate_chunk_size(size)

            while retry_count <= DEFAULT_RETRY_READ_LIMIT:
                try:
                    while chunk := response.read(min(fetch_size, chunk_size) if fetch_size else chunk_size):
                        total_fetched += len(chunk)
                        if fetch_size and total_fetched > fetch_size:
                            chunk = chunk[:fetch_size - total_fetched]
                            chunks.append(chunk)
                            break
                        chunks.append(chunk)
                    break
                except Exception as e:
                    print(f'Error while reading file: {str(e)} - Retrying.....({retry_count}/{DEFAULT_RETRY_READ_LIMIT})')
                    retry_count += 1

            name = os.path.basename(file_path)
            mime_type = response.info().get_content_type() or DEFAULT_FALLBACK_MIMETYPE
            base64_data = base64.b64encode(b''.join(chunks)).decode('utf-8')
            return name, mime_type, size, base64_data

    @staticmethod
    def read_local_file(
        file_path: str,
        fetch_size: int = None
    ) -> tuple[str, str, int, str]:
        """
        Fetches the content of a local file and returns it as a mime type,
        base64-encoded string, with an optional fetch size limit.

        Args:
            file_path (str): The path to the local file.
            fetch_size (int, optional): The maximum size to fetch from the file, in bytes.

        Returns:
            Tuple of information about the file:
                - mime_type: The mime type of the file.
                - base64_encoded_content: The base64-encoded content of the file.
                - size: The size of the file in bytes.
                - name: The name of the file.

        Example:
            >>> read_local_file("/path/to/file.txt", fetch_size=1024)
            ("file.txt", "text/plain", 4096, "SGVsbG8sIHdvcmxkIQ==")
        """
        def file_to_base64_streaming(file_path: str, fetch_size: int) -> Generator[str, None, None]:
            """
            Converts a file to a base64-encoded string generator with fetch size limit.

            Args:
                file_path (str): The path to the file.
                fetch_size (int): The maximum size to fetch from the file, in bytes.

            Yields:
                str: A base64-encoded string of the file data.
            """
            with open(file_path, "rb") as file:
                total_fetched = 0
                retry_count = 1
                while retry_count <= DEFAULT_RETRY_READ_LIMIT:
                    try:
                        while chunk := file.read(min(fetch_size, chunk_size) if fetch_size else chunk_size):
                            total_fetched += len(chunk)
                            if fetch_size and total_fetched > fetch_size:
                                chunk = chunk[:fetch_size - total_fetched]
                                yield chunk
                                break
                            yield chunk
                        break
                    except Exception as e:
                        print(f'Error while reading file: {str(e)} - Retrying.....({retry_count}/{DEFAULT_RETRY_READ_LIMIT})')
                        retry_count += 1

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if fetch_size and fetch_size <= 0:
            raise ValueError("`fetch_size` must be greater than 0 if provided.")

        name = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        chunk_size = calculate_chunk_size(size)
        mime_type = mimetypes.guess_type(file_path)[0] or DEFAULT_FALLBACK_MIMETYPE
        base64_data = base64.b64encode(b''.join(file_to_base64_streaming(file_path, fetch_size))).decode('utf-8')
        return name, mime_type, size, base64_data

    @staticmethod
    def read_file(
        file_path: str,
        fetch_size: int = None
    ) -> tuple[str, str, int, str]:
        """
        Fetches the content of a filepath or URL and returns it as a mime type,
        base64-encoded string, with an optional fetch size limit.

        Args:
            file_path (str): The path to the file or URL.
            fetch_size (int, optional): The maximum size to fetch from the file, in bytes.

        Returns:
            Tuple of information about the file:
                - mime_type: The mime type of the file.
                - base64_encoded_content: The base64-encoded content of the file.
                - size: The size of the file in bytes.
                - name: The name of the file.

        Example:
            >>> read_file("/path/to/file.txt", fetch_size=1024)
            ("file.txt", "text/plain", 4096, "SGVsbG8sIHdvcmxkIQ==")
            >>> read_file("https://example.com/file.txt", fetch_size=1024)
            ("file.txt", "text/plain", 4096, "SGVsbG8sIHdvcmxkIQ==")
        """
        if file_path.startswith("http://") or file_path.startswith("https://"):
            return FileBase64Encoder.read_remote_file(file_path, fetch_size)
        else:
            return FileBase64Encoder.read_local_file(file_path, fetch_size)
