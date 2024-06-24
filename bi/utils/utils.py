import re


def slugify(text):
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = re.sub(r'\s+', '-', text).strip()
    return text[:100]
