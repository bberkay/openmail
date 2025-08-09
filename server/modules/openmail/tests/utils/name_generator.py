import uuid

class NameGenerator:
    """Utility class for generating random names"""

    @staticmethod
    def name(
        prefix: str,
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate a random name with UUID

        Args:
            prefix (str): The prefix of the name
            count (int, optional): The number of names to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique names. Defaults to False.

        Returns:
            list[str]: A list of generated names.

        Example:
            >>> NameGenerator.name("openmail-test-", count=3, all_different=True)
            ['openmail-test-4A2B3C', 'openmail-test-5A2B3C', 'openmail-test-6A2B3C']
        """
        ids = []
        while len(ids) < count:
            unique_id = f"{prefix}{uuid.uuid4().hex[:6].upper()}"
            if not all_different or unique_id not in ids:
                ids.append(unique_id)

        return ids

    @staticmethod
    def folder_name(
        prefix="openmail-folder-test-",
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate a random folder name with given prefix
        and random UUID

        Args:
            prefix (str, optional): The prefix of the folder name. Defaults to "openmail-folder-test-".
            count (int, optional): The number of folder names to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique folder names. Defaults to False.

        Returns:
            list[str]: A list of generated folder names

        Example:
            >>> NameGenerator.folder_name(count=3, all_different=True)
            ['openmail-folder-test-4A2B3C', 'openmail-folder-test-5A2B3C', 'openmail-folder-test-6A2B3C']
        """
        return NameGenerator.name(
            prefix,
            count,
            all_different
        )

    @staticmethod
    def subject(
        prefix="openmail-subject-test-",
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate a random subject with given prefix
        and random UUID

        Args:
            prefix (str, optional): The prefix of the subject. Defaults to "openmail-subject-test-".
            count (int, optional): The number of subjects to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique subjects. Defaults to False.

        Returns:
            list[str]: A list of generated subjects

        Example:
            >>> NameGenerator.subject(count=3, all_different=True)
            ['openmail-subject-test-4A2B3C', 'openmail-subject-test-5A2B3C', 'openmail-subject-test-6A2B3C']
        """
        return NameGenerator.name(
            prefix,
            count,
            all_different
        )

    @staticmethod
    def body(
        prefix="openmail-body-test-",
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate a random body with given prefix
        and random UUID

        Args:
            prefix (str, optional): The prefix of the body. Defaults to "openmail-body-test-".
            count (int, optional): The number of bodies to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique bodies. Defaults to False.

        Returns:
            list[str]: A list of generated bodies

        Example:
            >>> NameGenerator.body(count=3, all_different=True)
            ['openmail-body-test-4A2B3C', 'openmail-body-test-5A2B3C', 'openmail-body-test-6A2B3C']
        """
        return NameGenerator.name(
            prefix,
            count,
            all_different
        )
