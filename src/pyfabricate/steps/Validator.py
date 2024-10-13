
from re import match as regExMatch

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


def validateEmail(email: str) -> bool:

    if regExMatch(EMAIL_REGEX, email):
        return True
    else:
        return False
