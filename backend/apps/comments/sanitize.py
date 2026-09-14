from urllib.parse import urlparse

import bleach
from django.conf import settings
from lxml import etree


class InvalidXHTML(ValueError):
    pass


# checked on the raw input: bleach would quietly close a dangling tag and hide the error
def sanitize(raw):
    parser = etree.XMLParser(resolve_entities=False)
    try:
        root = etree.fromstring(f'<comment>{raw}</comment>', parser=parser)
    except etree.XMLSyntaxError as e:
        raise InvalidXHTML(f'Not valid XHTML: {e.msg}') from e
    for el in root.iter('*'):
        if el is root:
            continue
        if el.tag not in settings.COMMENTS_ALLOWED_TAGS:
            raise InvalidXHTML(f'<{el.tag}> is not an allowed tag.')
        extra = set(el.attrib) - set(settings.COMMENTS_ALLOWED_ATTRS.get(el.tag, []))
        if extra:
            raise InvalidXHTML(f'<{el.tag}> must not carry {", ".join(sorted(extra))}.')
        scheme = urlparse(el.get('href', '')).scheme
        if scheme and scheme not in settings.COMMENTS_ALLOWED_PROTOCOLS:
            raise InvalidXHTML(f'{scheme}: links are not allowed.')
    return bleach.clean(
        raw,
        tags=settings.COMMENTS_ALLOWED_TAGS,
        attributes=settings.COMMENTS_ALLOWED_ATTRS,
        protocols=settings.COMMENTS_ALLOWED_PROTOCOLS,
        strip=True,
    )
