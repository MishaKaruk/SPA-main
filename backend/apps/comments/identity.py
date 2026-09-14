from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

FIELDS = ('name', 'email', 'homepage')


# signed identity of a visitor who has no account: it saves retyping the form and lets the
# server take the author from a signature instead of free-form input on every post
class IdentityToken(AccessToken):
    token_type = 'identity'
    lifetime = settings.COMMENTS_IDENTITY_LIFETIME


def issue(comment):
    token = IdentityToken()
    token['name'] = comment.author_name
    token['email'] = comment.author_email
    token['homepage'] = comment.author_homepage
    return str(token)


def read(raw):
    try:
        token = IdentityToken(raw)
    except TokenError:
        return None
    return {f: token.payload.get(f, '') for f in FIELDS}
