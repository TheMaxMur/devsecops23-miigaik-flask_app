import pathlib, os

from flask import Flask

from dip.extensions import db, migrate
from dip.models import User
from dip.utils.security import generate_password_hash
from dip import views


def create_admin_user(db, config):
    admin = User.query.filter_by(username='admin').first()

    if not admin:

        password = generate_password_hash(
            config['ADMIN']['password'],
            config['PASSWORD_SALT']
            )

        print('admin password: {}'.format(password))

        admin = User(
            username=config['ADMIN']['username'],
            password=password,
            email=config['ADMIN']['email'],
            role='admin'
            )
        db.session.add(admin)
        try:
            db.session.commit()
        except:
            print("User alredy exist")

    return


def register_blueprints(app):
    app.register_blueprint(views.bp_user)
    app.register_blueprint(views.bp_auth)
    app.register_blueprint(views.bp_admin)
    app.register_blueprint(views.bp_wiki)
    app.register_blueprint(views.bp_index)
    
    app.register_blueprint(views.bp_static)



def create_app():
    app = Flask(__name__)

    FLASK_SETTINGS = os.environ.get("FLASK_SETTINGS", "settings_local.LocalConfig")

    app.config.from_object(FLASK_SETTINGS)

    if FLASK_SETTINGS == "settings_local.LocalConfig":
        pathlib.Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(app.config['DATABASE_PATH']).touch(exist_ok=True)

    for path in app.config['PATHS'].values():
        path.mkdir(parents=True, exist_ok=True)


    db.init_app(app)
    migrate.init_app(app, db)


    with app.app_context():
        db.create_all()
        create_admin_user(db, app.config)

    register_blueprints(app)

    return app