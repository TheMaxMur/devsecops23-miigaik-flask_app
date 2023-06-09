from flask import Blueprint, make_response, render_template, request, url_for, redirect, jsonify, current_app
import re

from dip.extensions import db
from dip.utils.session import set_user_identity, admin_only
from dip.utils.models import user_to_json
from dip.utils.security import ALLOWED_IMAGE_EXTENSIONS, generate_password_hash, remove_image_metadata
from dip.models import JobTitle, User

bp = Blueprint('bp_admin', __name__)

MAGIC_NUMBERS = { 'png': bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
                  'jpg': bytes([0xFF, 0xD8, 0xFF, 0xE0]),
                  'jpeg': bytes([0xFF, 0xD8, 0xFF, 0xDB]),
                  'jpeg-jfif': bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01]),
                  'jpeg1': bytes([0xFF, 0xD8, 0xFF, 0xEE]),
                }

def validate_string(input_string: str) -> bool:
    if not (re.match("^[a-zA-Zа-яА-Я0-9@.]+$", input_string)):
        return False
    if (len(input_string) > 50):
        return False
    return True

def validate_phone(phone_string: str) -> bool:
    if (len(phone_string) <= 12):
        return re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', phone_string)
    return False

@bp.route('/admin/dashboard/users', methods=['GET'])
@admin_only
def users():

    users = User.query.all()
    job_titles = JobTitle.query.all()

    return render_template('admin_dashboard_users.html', users=users, roles=current_app.config['ROLES'], job_titles=job_titles)


@bp.route('/admin/dashboard/user/<id_>', methods=['GET'])
@admin_only
def user(id_):
    user = User.query.filter_by(id=id_).first()

    if not user:
        return f'Пользователь с id {id_} не найден', 404

    return jsonify(user.json())


@bp.route('/admin/dashboard/user/<id_>/update', methods=['PUT', 'POST'])
@admin_only
def user_update(id_):
    user = User.query.filter_by(id=id_).first()

    if not user:
        return f'Пользователь с id {id_} не найден', 404

    user_data = request.form

    exists_username = User.query.filter_by(
        username=user_data.get('username')).first()

    if exists_username and user.username != user_data.get('username'):
        return f'Пользователь с именем {user_data.get("username")} уже существует', 409

    exists_email = User.query.filter_by(email=user_data.get("email")).first()

    if exists_email and user.email != user_data.get('email'):
        return f'Пользователь с email {user_data.get("username")} уже существует', 409

    if user_data.get('role') not in current_app.config['ROLES']:
        return f'Роль {user_data.get("role")} не найдена', 404

    jt = JobTitle.query.filter_by(id=user_data.get("job_title")).first()

    if not jt and user.role != 'admin':
        return f'Должность {user_data.get("job_title")} не найдена', 404

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

        user.photo = photo_file.filename

    if user_data.get('password'):
        user.password = generate_password_hash(user_data.get(
            'password'), current_app.config['PASSWORD_SALT'])

    user.username = user_data.get('username')
    user.first_name = user_data.get('first_name')
    user.second_name = user_data.get('second_name')
    user.patronymic = user_data.get('patronymic')
    user.email = user_data.get('email')
    user.phone_number = user_data.get('phone_number')
    user.role = user_data.get('role')
    user.job_title = JobTitle.query.filter_by(
        id=user_data.get("job_title")).first()

    # Validation

    if not validate_string(user.username):
        return f'Username введен некорректно', 409
    if not validate_string(user.first_name):
        return f'Имя введено некорректно', 409
    if not validate_string(user.second_name):
        return f'Фамилия введена некорректно', 409
    if not validate_string(user.patronymic):
        return f'Отчество введено некорректно', 409
    if not validate_string(user.email):
        return f'Email введен некорректно', 409
    if not validate_string(user.role):
        return f'Название роли введено некорректно', 409
    if not validate_phone(user.phone_number):
        return f'Некорректный номер телефона', 409

    db.session.commit()

    return redirect(url_for('bp_admin.users'))


@bp.route('/admin/dashboard/user/create', methods=['PUT', 'POST'])
@admin_only
def user_create():

    user = User()

    user_data = request.form

    exists_username = User.query.filter_by(
        username=user_data.get('username')).first()

    if exists_username and user.username != user_data.get('username'):
        return f'Пользователь с именем {user_data.get("username")} уже существует', 409

    exists_email = User.query.filter_by(email=user_data.get("email")).first()

    if exists_email and user.email != user_data.get('email'):
        return f'Пользователь с email {user_data.get("username")} уже существует', 409

    if user_data.get('role') not in current_app.config['ROLES']:
        return f'Роль {user_data.get("role")} не найдена', 404

    jt = JobTitle.query.filter_by(id=user_data.get("job_title")).first()

    user.role = user_data.get('role')

    if not jt and user.role != 'admin':
        return f'Должность {user_data.get("job_title")} не найдена', 404

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

        user.photo = photo_file.filename

    if not user_data.get('password'):
        return f'Пароль не указан', 400

    user.username = user_data.get('username')
    user.first_name = user_data.get('first_name')
    user.second_name = user_data.get('second_name')
    user.patronymic = user_data.get('patronymic')
    user.email = user_data.get('email')
    user.phone_number = user_data.get('phone_number')
    user.job_title = JobTitle.query.filter_by(
        id=user_data.get("job_title")).first()

    user.password = generate_password_hash(user_data.get(
        'password'), current_app.config['PASSWORD_SALT'])

    if not validate_string(user.username):
        return f'Username введен некорректно', 409
    if not validate_string(user.first_name):
        return f'Имя введен некорректно', 409
    if not validate_string(user.second_name):
        return f'Фамилия введен некорректно', 409
    if not validate_string(user.patronymic):
        return f'Отчество введен некорректно', 409
    if not validate_string(user.email):
        return f'Email введен некорректно', 409
    if not validate_string(user.role):
        return f'Название роли введен некорректно', 409
    if not validate_phone(user.phone_number):
        return f'Некорректный номер телефона', 409

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('bp_admin.users'))


@bp.route('/admin/dashboard/user/<id_>/delete', methods=['GET', 'POST'])
@admin_only
def user_delete(id_):
    if id_ == "1":
        return f'Невозможно удалить пользователя, потому что он является корневым', 409

    user = User.query.filter_by(id=id_).first()

    if not user:

        return f'Пользователь с id {id_} не найдена', 404

    db.session.delete(user)
    db.session.commit()

    return 'ok', 200


@bp.route('/admin/dashboard/job-titles', methods=['GET', 'POST'])
@admin_only
def job_titles():

    job_titles = JobTitle.query.all()

    if request.method == 'GET':
        return render_template('admin_dashboard_job_titles.html', job_titles=job_titles)

    job_title = request.form.get('job_title')

    if not job_title:
        return render_template('admin_dashboard_job_titles.html', error='Не указана должность', job_titles=job_titles)

    job_title_exists = JobTitle.query.filter_by(title=job_title).first()

    if job_title_exists:
        return render_template('admin_dashboard_job_titles.html', error='Должность уже существует', job_titles=job_titles)

    job_title = JobTitle(title=job_title)
    db.session.add(job_title)
    db.session.commit()

    job_titles = JobTitle.query.all()

    return redirect(url_for('bp_admin.job_titles'))
    # return render_template('admin_dashboard_job_titles.html', job_titles=job_titles), 200


@bp.route('/admin/dashboard/job-titles/<id_>/delete', methods=['GET', 'POST'])
@admin_only
def job_title_delete(id_):

    job_title = JobTitle.query.filter_by(id=id_).first()

    if not job_title:
        return f'Должность с id {id_} не найдена', 404

    if job_title.users:
        return f'Невозможно удалить должность, поскольку она закреплена за пользователями', 409

    db.session.delete(job_title)
    db.session.commit()

    return 'ok', 200


@bp.route('/admin/dashboard/job-titles/<id_>/update', methods=['PUT'])
@admin_only
def job_title_update(id_):
    new_job_title = request.get_json()

    job_title = JobTitle.query.filter_by(id=id_).first()

    job_title_exists = JobTitle.query.filter_by(
        title=new_job_title['title']).first()

    if job_title_exists:
        return f'Должность с названием {new_job_title["title"]} уже существует', 409

    job_title.title = new_job_title['title']
    db.session.commit()

    return 'ok', 200
