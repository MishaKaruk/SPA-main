import secrets

from django.conf import settings

# no l, o, 0 or 1: they are impossible to tell apart once the image is distorted
CHARS = 'abcdefghijkmnpqrstuvwxyz23456789'


def alnum_challenge():
    word = ''.join(secrets.choice(CHARS) for _ in range(settings.CAPTCHA_LENGTH))
    return word.upper(), word
