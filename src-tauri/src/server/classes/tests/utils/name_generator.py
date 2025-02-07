import uuid

class NameGenerator:
    """Utility class for generating random names"""

    @staticmethod
    def name(
        prefix: str,
        suffix: str = "",
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate a random name with UUID

        Args:
            prefix (str): The prefix of the name
            suffix (str, optional): The suffix to append at the end of the name. Defaults to "".
            count (int, optional): The number of names to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique names. Defaults to False.

        Returns:
            list[str]: A list of generated names.

        Example:
            >>> NameGenerator.name("alex", "domain", count=3, all_different=True)
            ['alex4A2B3Cdomain', 'alex5A2B3Cdomain', 'alex6A2B3Cdomain']
        """
        ids = []
        while len(ids) < count:
            unique_id = f"{prefix}{uuid.uuid4().hex[:6].upper()}{suffix}"
            if not all_different or unique_id not in ids:
                ids.append(unique_id)

        return ids[0] if len(ids) == 1 else ids

    @staticmethod
    def email_address(
        prefix="alex",
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate a random email address with given prefix
        and random UUID

        Args:
            prefix (str, optional): The prefix of the folder name. Defaults to "name".
            count (int, optional): The number of folder names to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique folder names. Defaults to False.

        Returns:
            list[str]: A list of generated folder names

        Example:
            >>> NameGenerator.email_address(count=3, all_different=True)
            ['name4A2B3C@domain.com', 'name5A2B3C@domain.com', 'name6A2B3C@domain.com']
        """
        return NameGenerator.name(
            prefix,
            "@domain.com",
            count,
            all_different
        )

    @staticmethod
    def fullname(
        prefix="Full Name ",
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate a random fullname with given prefix
        and random UUID

        Args:
            prefix (str, optional): The prefix of the subject. Defaults to "Full Name ".
            count (int, optional): The number of subjects to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique subjects. Defaults to False.

        Returns:
            list[str]: A list of generated subjects

        Example:
            >>> NameGenerator.fullname(count=3, all_different=True)
            ['Full Name 4A2B3C', 'Full Name 5A2B3C', 'Full Name 6A2B3C']
        """
        return NameGenerator.name(
            prefix,
            "",
            count,
            all_different
        )

    @staticmethod
    def password(
        prefix="psw-",
        count: int = 1,
        all_different: bool = False
    ) -> list[str]:
        """
        Generate a random password with given prefix
        and random UUID

        Args:
            prefix (str, optional): The prefix of the body. Defaults to "psw-".
            count (int, optional): The number of bodies to generate. Defaults to 1.
            all_different (bool, optional): If True, generate unique bodies. Defaults to False.

        Returns:
            list[str]: A list of generated bodies

        Example:
            >>> NameGenerator.password(count=3, all_different=True)
            ['psw-4A2B3C', 'psw-5A2B3C', 'psw-6A2B3C']
        """
        return NameGenerator.name(
            prefix,
            "",
            count,
            all_different
        )
