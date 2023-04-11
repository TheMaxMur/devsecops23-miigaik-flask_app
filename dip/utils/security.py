import hmac
import hashlib
import pathlib
from pathlib import Path
from flask import current_app
from PIL import Image


ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Список допустимых тегов и подтегов
ALLOWED_TAGS = {
    '0th': set(['Make', 'Model', 'Software']),
    'Exif': set(),
    'Interop': set(),
    'GPS': set(),
    '1st': set()
}


def remove_image_metadata(filename):
    filepath = Path(current_app.root_path).parent / \
        current_app.config["PATHS"]["user_images"] / filename

    # валидация файлового пути
    if not filepath.is_file():
        return
    
    image = Image.open(str(filepath))

    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    image_without_exif.save(str(filepath))


def generate_password_hash(password, salt):
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()


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


# из девелопа
'''
def remove_image_metadata(filename):
    # ? filepath = pathlib.Path(current_app.root_path).parent / \
    filepath = pathlib.Path(current_app.root_path).parent / \
        current_app.config["PATHS"]["user_images"] / filename

    command = f'exiftool -EXIF= { filepath }'

    # os.system(command)
    subprocess.run(command)
'''
