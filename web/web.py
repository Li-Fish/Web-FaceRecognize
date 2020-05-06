from flask import Flask, render_template, make_response, request

from util.account_util import generate_auth_token, decode_auth_token
from util.database_engine import DatabaseEngine
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

from util.fish_logger import log

secret_key = "magic"
auth = HTTPBasicAuth()
db = DatabaseEngine()
app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
CORS(app, supports_credentials=True)


@app.after_request
def after_request(resp):
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'content-type,token'
    return resp


@auth.verify_password
def verify_password(fir, sec):
    username_token = request.headers.get('Token')
    if username_token is None or username_token == '':
        return False
    else:
        username = decode_auth_token(username_token, secret_key)
        return db.get_user_by_name(username) is not None


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/api/login', methods=['post'])
def login():
    json = request.get_json()
    log.info("receive json {}".format(json))
    user = db.get_user_by_name(json['username'])

    if user is None or 'password' not in json:
        return ''

    if user['password'] == json['password']:
        token = generate_auth_token(user['username'], 60 * 60 * 24, secret_key)
        return token
    return ""


@app.route('/api/attendance_table', methods=['post'])
@auth.login_required
def attendance_table():
    json = request.get_json()
    log.info("receive json {}".format(json))

    res = {}

    offset = (json['pageIndex'] - 1) * json['pageSize']
    limit = json['pageSize']
    title_prefix = json['title_prefix']

    res["list"], res["total_num"] = db.get_attendance_by_index(title_prefix, json['creator'], offset, limit)

    return res


@app.route('/api/update_attendance', methods=['post'])
@auth.login_required
def update_attendance():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.update_attendance(json['id'], json['title'], json['info'], json['type'])

    return 'OK'


@app.route('/api/delete_attendance', methods=['post'])
@auth.login_required
def delete_attendance():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.delete_attendance(json['id'])

    return 'OK'


@app.route('/api/attendance_user_table', methods=['post'])
@auth.login_required
def attendance_user_table():
    json = request.get_json()
    log.info("receive json {}".format(json))

    res = {}

    offset = (json['pageIndex'] - 1) * json['pageSize']
    limit = json['pageSize']
    name_prefix = json['name']
    attendance_title = json["attendance"]

    res["list"], res["total_num"] = db.get_attendance_user_by_index(name_prefix, attendance_title, offset, limit)

    return res


@app.route('/api/update_attendance_user', methods=['post'])
@auth.login_required
def update_attendance_user():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.update_attendance_user(json['id'], json['name'])

    return 'OK'


@app.route('/api/delete_attendance_user', methods=['post'])
@auth.login_required
def delete_attendance_user():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.delete_attendance_user(json['id'])

    return 'OK'


@app.route('/api/record_table', methods=['post'])
@auth.login_required
def record_table():
    json = request.get_json()
    log.info("receive json {}".format(json))

    res = {}

    offset = (json['pageIndex'] - 1) * json['pageSize']
    limit = json['pageSize']
    name_prefix = json['name']
    attendance_title = json["attendance"]

    res["list"], res["total_num"] = db.get_record_by_index(name_prefix, attendance_title, offset, limit)

    return res


@app.route('/api/delete_record', methods=['post'])
@auth.login_required
def delete_record():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.delete_record(json['id'])

    return 'OK'
