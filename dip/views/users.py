from flask import Blueprint, make_response, render_template, request, url_for, current_app, redirect

from dip.utils.session import set_user_identity, authed_only, get_current_user, role_required, set_user_if_authed
from dip.utils.security import remove_image_metadata, generate_password_hash
from dip.extensions import db
from dip.models import User

bp = Blueprint('bp_user', __name__)

MAGIC_NUMBERS = { 'png': bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
                  'jpg': bytes([0xFF, 0xD8, 0xFF, 0xE0]),
                  'jpeg': bytes([0xFF, 0xD8, 0xFF, 0xDB]),
                  'jpeg-jfif': bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01]),
                  'jpeg1': bytes([0xFF, 0xD8, 0xFF, 0xEE]),
                }

bp.before_app_request(set_user_if_authed)
bp.after_app_request(set_user_identity)


@bp.route('/profile', methods=['GET', 'POST'])
@authed_only
def profile():

    if request.method == 'GET':

        current_user = get_current_user()
        user_json = current_user.json()

        if user_json.get('photo'):
            user_json['photo'] = url_for(
                'static.send_user_image', id_=current_user.id)

        else:
            user_json['photo'] = url_for(
                'static', filename='img/profile-picture.jpg')

        return render_template('profile.html', user=user_json)

    else:
        current_user = get_current_user()
        user_json = current_user.json()

        user_data = request.form

        photo_file = request.files.get('photo')

        if photo_file.filename:
            filepath = current_app.config['PATHS']['user_images'] / \
                photo_file.filename

            if not filepath.exists():
                max_read_size = max(len(m) for m in MAGIC_NUMBERS.values())
                file_head = photo_file.read(max_read_size)

                flag = 0
                for ext in MAGIC_NUMBERS:
                    print(file_head.startswith(MAGIC_NUMBERS[ext]), file_head, MAGIC_NUMBERS[ext])
                    if file_head.startswith(MAGIC_NUMBERS[ext]):
                        photo_file.save(filepath)
                        with open(filepath, 'rb') as file:
                            content = file.read()

                        with open(filepath, 'wb') as file:
                            file.write(file_head)
                            file.write(content)

                        remove_image_metadata(photo_file.filename)
                        flag += 1
                        break

                if not flag:
                    return f'Нельзя загружать файлы данного типа', 403

            current_user.photo = photo_file.filename

        if user_data.get('password'):
            current_user.password = generate_password_hash(user_data.get(
                'password'), current_app.config['PASSWORD_SALT'])

        db.session.commit()

        return redirect(url_for('bp_user.profile'))

@bp.route('/profile/<username>', methods=['GET', 'POST'])
@role_required(['user', 'admin'])
def profile_username(username):
    if request.method == 'GET':

        user = User.query.filter_by(username=username).first()

        user_json = user.json()

        if user_json.get('photo'):
            user_json['photo'] = url_for(
                'static.send_user_image', id_=user.id)

        else:
            user_json['photo'] = url_for(
                'static', filename='img/profile-picture.jpg')

        return render_template('profile_id.html', user=user_json)
