import pathlib, os, requests, json

class DevConfig:
    BASE_URL = "https://vault.devsecops.maxmur.info"
    ROLE_ID = os.environ.get("ROLE_ID")
    SECRET_ID = os.environ.get("SECRET_ID")
    TOKEN = json.loads(requests.post(BASE_URL + '/v1/auth/approle/login', \
                        data={"role_id": ROLE_ID, "secret_id": SECRET_ID}).text)['auth']['client_token']

    SECRET_KEY = json.loads(requests.get(BASE_URL + '/v1/secret/dev/secret_key', \
                            headers={"X-Vault-Token": TOKEN}).text)['data']['SECRET_KEY']
    PASSWORD_SALT = json.loads(requests.get(BASE_URL + '/v1/secret/dev/password_salt', \
                            headers={"X-Vault-Token": TOKEN}).text)['data']['PASSWORD_SALT']
    
    DB_NAME = json.loads(requests.get(BASE_URL + '/v1/secret/dev/db_name', \
                            headers={"X-Vault-Token": TOKEN}).text)['data']['DB_NAME']

    DB_USER = json.loads(requests.get(BASE_URL + '/v1/secret/dev/db_user', \
                            headers={"X-Vault-Token": TOKEN}).text)['data']['DB_USER']

    DB_PASSWORD = json.loads(requests.get(BASE_URL + '/v1/secret/dev/db_password', \
                            headers={"X-Vault-Token": TOKEN}).text)['data']['DB_PASSWORD']

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@db:5432/{DB_NAME}"

    PATHS = {
        'user_md_files': pathlib.Path('user_md_files'),
        'user_documents': pathlib.Path('user_documents'),
        'user_images': pathlib.Path('user_images'),
    }

    ADMIN = {
        'username': json.loads(requests.get(BASE_URL + '/v1/secret/dev/admin_username', \
                            headers={"X-Vault-Token": TOKEN}).text)['data']['ADMIN_USERNAME'],
        'password': json.loads(requests.get(BASE_URL + '/v1/secret/dev/admin_password', \
                            headers={"X-Vault-Token": TOKEN}).text)['data']['ADMIN_PASSWORD'],
        'email': json.loads(requests.get(BASE_URL + '/v1/secret/dev/admin_email', \
                            headers={"X-Vault-Token": TOKEN}).text)['data']['ADMIN_EMAIL']
    }

    ROLES = [
        'admin',
        'user'
    ]
