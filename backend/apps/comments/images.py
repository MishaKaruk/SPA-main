from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image, ImageSequence

EXTENSIONS = {'JPEG': 'jpg', 'PNG': 'png', 'GIF': 'gif'}


# uploads keep only a slug of their name plus the extension of the format we actually detected,
# so a valid image cannot be served back as .html from the same origin
def stored_name(original, ext):
    stem = slugify(Path(original).stem)[:40]
    return f'{stem or "file"}.{ext}'


def fit(f):
    max_w, max_h = settings.COMMENTS_MAX_IMAGE_SIZE
    img = Image.open(f)
    if img.width <= max_w and img.height <= max_h:
        f.seek(0)
        return None
    scale = min(max_w / img.width, max_h / img.height)
    size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    buf = BytesIO()
    if img.format == 'GIF' and getattr(img, 'n_frames', 1) > 1:
        frames = [
            frame.convert('RGBA').resize(size, Image.LANCZOS)
            for frame in ImageSequence.Iterator(img)
        ]
        frames[0].save(
            buf, format='GIF', save_all=True, append_images=frames[1:], disposal=2,
            loop=img.info.get('loop', 0), duration=img.info.get('duration', 100),
        )
    else:
        fmt = img.format if img.format in ('PNG', 'GIF') else 'JPEG'
        if fmt == 'JPEG' and img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize(size, Image.LANCZOS)
        img.save(buf, format=fmt, optimize=True)
    f.seek(0)
    return ContentFile(buf.getvalue(), name=f.name)
