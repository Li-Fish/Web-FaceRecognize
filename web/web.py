import base64
import os
import json as js
from flask import Flask, render_template, make_response, request, g
from util.account_util import generate_auth_token, decode_auth_token
from util.common_tools import bin_to_array, array_to_bin
from util.database_engine import DatabaseEngine
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from util.fish_socket import ClientSocket

from util.fish_logger import log

base_img_path = '/home/fish/PycharmProjects/Web&FaceRecognize/images/'
upload_path = base_img_path + '/upload_image/'

face_server_address = ('192.168.123.136', 11234)
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
        g.username = username
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


@app.route('/api/add_attendance', methods=['post'])
@auth.login_required
def add_attendance():
    json = request.get_json()
    log.info("receive json {}".format(json))

    user_id = db.get_user_by_name(g.username)['id']

    db.insert_attendance(json['title'], user_id, json['info'], json['type'])

    return 'OK'


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


@app.route('/api/add_attendance_user', methods=['post'])
@auth.login_required
def add_attendance_user():
    json = js.loads(request.form.get('json'))
    log.info("receive json {}".format(json))

    img_data = request.files['file'].read()
    print(img_data[:10])

    socket = ClientSocket.connect_socket(face_server_address[0], face_server_address[1])

    # request type
    socket.send(b'1')
    socket.send(img_data)

    feature = socket.raw_recv()

    if len(feature) == 0:
        app.logger.info('FE fail')
        return 'FE Fail', 500

    img_path = upload_path + base64.b64encode(bytes(json['name'], encoding='utf8')).decode() + '.jpg'
    log.info('save img, path: {}'.format(img_path))

    with open(img_path, 'wb') as f:
        f.write(img_data)

    feature = array_to_bin(feature)
    db.insert_attendance_user(json["name"], img_path, feature, json['attendance_id'])

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


@app.route('/api/upload_attendance_date', methods=['post'])
@auth.login_required
def upload_attendance_date():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.upload_attendance_date(json['date_list'], json['attendance_id'], json['week_list'])

    return 'OK'


@app.route('/api/get_attendance_date', methods=['post'])
@auth.login_required
def get_attendance_date():
    json = request.get_json()
    log.info("receive json {}".format(json))
    time_list, week_list = db.get_attendance_date(json['attendance_id'])
    res = {'time_list': time_list,
           'week_list': week_list}
    return res


@app.route('/api/change_attendance_code', methods=['post'])
@auth.login_required
def change_attendance_code():
    json = request.get_json()
    log.info("receive json {}".format(json))
    db.update_attendance_code(json['id'])
    return 'OK'


@app.route('/api/get_dashboard_data', methods=['post'])
@auth.login_required
def get_dashboard_data():
    rst = {}
    rst['attendance_list'] = db.get_recent_record()
    rst['today_attendance_num'] = db.get_today_attendance_num()
    rst['last_7days_attendance_num'] = db.get_last_7days_attendance_num()
    return rst


@app.route('/api/image/<string:image_dir>/<file_name>', methods=['post', 'get'])
# @auth.login_required
def get_photo(image_dir, file_name):
    print(image_dir, file_name)

    image_data = open(base_img_path + image_dir + '/' + file_name, 'rb').read()
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'

    return response


@app.route('/api/manager_user_table', methods=['post'])
@auth.login_required
def manager_user_table():
    json = request.get_json()
    log.info("receive json {}".format(json))

    res = {}

    offset = (json['pageIndex'] - 1) * json['pageSize']
    limit = json['pageSize']
    name_prefix = json['username']

    res["list"], res["total_num"] = db.get_manager_user_by_index(name_prefix, offset, limit)

    return res


@app.route('/api/delete_manager_user', methods=['post'])
@auth.login_required
def delete_manager_user():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.delete_manager_user(json['id'])

    return 'OK'


@app.route('/api/update_manager_user', methods=['post'])
@auth.login_required
def update_manager_user():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.update_manager_user(json['id'], json['username'], json['password'])

    return 'OK'


@app.route('/api/add_manager_user', methods=['post'])
@auth.login_required
def add_manager_user():
    json = request.get_json()
    log.info("receive json {}".format(json))

    db.insert_manager_user(json['username'], json['password'], 2)

    return 'OK'