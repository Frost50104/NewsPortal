import re
from django import template

register = template.Library()

# Define a set of undesirable words (lowercase). Adjust as needed.
BAD_WORDS = {
    'редиска',
    'дурак',
    'идиот',
    'плохой',
    'плохое',
    'плохая',
}


def _mask_word(match: re.Match) -> str:
    word = match.group(0)
    # Replace all letters (cyrillic/latin) with '*', keep other chars as is
    return re.sub(r"[A-Za-zА-Яа-яЁё]", "*", word)


@register.filter(name='censor')
def censor(value: str) -> str:
    """
    Replaces letters of undesirable words in the given text with '*'.
    Matching is case-insensitive and respects word boundaries.
    Example: "Этот дурак" -> "Этот *****"
    """
    if not isinstance(value, str) or not value:
        return value

    # Build regex with word boundaries for each bad word
    escaped = [re.escape(w) for w in BAD_WORDS]
    if not escaped:
        return value
    pattern = r"\b(" + "|".join(escaped) + r")\b"

    return re.sub(pattern, _mask_word, value, flags=re.IGNORECASE | re.UNICODE)
