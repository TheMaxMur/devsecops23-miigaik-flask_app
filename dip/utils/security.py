import hmac
import hashlib
import pathlib

from pathlib import Path
# from pyexiftool import exiftool  # Хули он подчеркивается я же скачал пипом
import piexif
from flask import current_app


ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Список допустимых тегов
# ALLOWED_TAGS = {'EXIF:Make', 'EXIF:Model', 'EXIF:Software'}
ALLOWED_TAGS = {'0th', 'Exif', 'Interop', 'GPS', '1st'}


def generate_password_hash(password, salt):
    return hashlib.md5((password + salt).encode('utf-8')).hexdigest()


def is_correct_password(plain_password, hashed_password, salt):

    return generate_password_hash(plain_password, salt) == hashed_password


def is_valid_signature(identity, secret_key):

    username = identity.get('username', '')
    role = identity.get('role', '')

    signature = identity.get('signature', '')

    return hmac.compare_digest(
        signature,
        create_signature(username, role, secret_key)
    )


def create_signature(username, role, secret_key):
    msg = username + role

    signature = hmac.new(
        secret_key.encode('utf-8'),
        msg.encode('utf-8'), hashlib.sha256
    ).hexdigest()

    return signature


def remove_image_metadata(filename):
    filepath = Path(current_app.root_path).parent / \
        current_app.config["PATHS"]["user_images"] / filename

    # валидация файлового пути
    if not filepath.is_file():
        return

    img = piexif.load(str(filepath))
    for ifd in img:
        if ifd in ALLOWED_TAGS:
            for tag in img[ifd]:
                if tag not in ALLOWED_TAGS[ifd]:
                    img[ifd][tag] = piexif.ExifIFD[tag].default_value

    exif_bytes = piexif.dump(img)
    piexif.insert(exif_bytes, str(filepath))


# Был бы ты человек
'''
def remove_image_metadata(filename):
    filepath = Path(current_app.root_path).parent / \
        current_app.config["PATHS"]["user_images"] / filename

    # валидация файлового пути
    if not filepath.is_file():
        return

    with exiftool.ExifTool() as et:
        et.execute(b'-EXIF:Make', b'-EXIF:Model',
                   b'-EXIF:Software', str(filepath))
'''
