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
    print(resp)
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'content-type,token'
    return resp


@auth.verify_password
def verify_password(fir, sec):
    username_token = request.headers.get('Token')
    print(username_token)
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
    log.info("receive json {}", json)
    user = db.get_user_by_name(json['username'])

    if user is None or 'password' not in json:
        return ''

    if user['password'] == json['password']:
        token = generate_auth_token(user['username'], 10, secret_key)
        return token
    return ""


simple_data = '''
{
    "list": [{
            "id": 1,
            "name": "张三",
            "money": 123,
            "address": "广东省东莞市长安镇",
            "state": "成功",
            "date": "2019-11-1",
            "thumb": "https://lin-xin.gitee.io/images/post/wms.png"
        },
        {
            "id": 2,
            "name": "李四",
            "money": 456,
            "address": "广东省广州市白云区",
            "state": "成功",
            "date": "2019-10-11",
            "thumb": "https://lin-xin.gitee.io/images/post/node3.png"
        },
        {
            "id": 3,
            "name": "王五",
            "money": 789,
            "address": "湖南省长沙市",
            "state": "失败",
            "date": "2019-11-11",
            "thumb": "https://lin-xin.gitee.io/images/post/parcel.png"
        },
        {
            "id": 4,
            "name": "赵六",
            "money": 1011,
            "address": "福建省厦门市鼓浪屿",
            "state": "成功",
            "date": "2019-10-20",
            "thumb": "https://lin-xin.gitee.io/images/post/notice.png"
        }
    ],
    "pageTotal": 4
}
'''


@app.route('/api/table', methods=['post'])
@auth.login_required
def table():
    print('2333')
    return simple_data
