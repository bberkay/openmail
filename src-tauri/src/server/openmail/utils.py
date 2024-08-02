import datetime

def extract_domain(email: str) -> str:
    return email.split('@')[1].split(".")[0]

def convert_to_imap_date(date: str) -> str:
    # 1970-01-01 to 01-Jan-1970
    # https://datatracker.ietf.org/doc/html/rfc5322#section-3.3
    return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d-%b-%Y')

def choose_positive(var1: int, var2: int) -> int:
    return var1 if var1 > 0 else var2

def contains_non_ascii(string: str) -> bool:
    return any(ord(char) > 127 for char in string)

def make_size_human_readable(size: int | None) -> str:
    if size is None:
        return "0 B"
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / 1024 / 1024:.2f} MB"
    else:
        return f"{size / 1024 / 1024 / 1024:.2f} GB"
