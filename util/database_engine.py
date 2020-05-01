import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from face.face_engine import FaceEngine
from util.database_model import Base, AttendanceUser, Attendance, ManageUser, Photo, Feature
from util.common_tools import bin_to_array, array_to_bin


class DatabaseEngine:
    def __init__(self, args=None):
        if args is None:
            args = self.get_simple_args()

        connect_str = 'mysql+mysqldb://{}:{}@{}:{}/{}' \
            .format(args['username'], args['password'], args['host'], args['port'], args['db'])

        self.engine = create_engine(connect_str, echo=False)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    def init_db(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def get_retrieve_user(self, attendance_id):
        session = self.Session()
        rst = []
        for user in session.query(AttendanceUser).filter_by(attendance_id=attendance_id):
            rst.append({
                'id': user.id,
                'name': user.name,
                'feature': bin_to_array(user.feature)
            })
        return rst

    def get_user_by_name(self, username):
        session = self.Session()
        for user in session.query(ManageUser).filter_by(username=username):
            return {
                "id": user.id,
                "username": user.username,
                "password": user.password,
                "type": user.type
            }
        return None

    def get_attendance_by_title(self, title):
        session = self.Session()
        for item in session.query(Attendance).filter_by(title=title):
            return {
                "id": item.id,
                "creator_id": item.creator_id,
                "title": item.title,
                "type": item.type,
                "info": item.info
            }
        return None

    def insert_attendance(self, title, create_id=None, info=None, _type=1):
        item = Attendance()
        item.title = title
        item.creator_id = create_id
        item.info = info
        item.type = _type

        session = self.Session()
        session.add(item)
        session.commit()
        session.close()

    def insert_attendance_user(self, name, photo_src, feature_array, attendance_id):
        photo = Photo()
        photo.src_path = photo_src

        feature = Feature()
        feature.photo = photo
        feature.data = array_to_bin(feature_array)

        item = AttendanceUser()
        item.name = name
        item.feature = feature
        item.photo = photo
        item.attendance_id = attendance_id

        session = self.Session()
        session.add(item)
        session.commit()
        session.close()

    def insert_manager_user(self, username, password, _type=1):
        item = ManageUser()
        item.username = username
        item.password = password
        item.type = _type

        session = self.Session()
        session.add(item)
        session.commit()
        session.close()

    @staticmethod
    def get_simple_args():
        args = {
            'username': 'root',
            'password': '109412',
            'host': '127.0.0.1',
            'port': 3306,
            'db': 'face'
        }
        return args


def fake_data(db_engine):
    face_engine = FaceEngine()
    db_engine.init_db()
    db_engine.insert_manager_user("fish", "123456")
    create_id = db_engine.get_user_by_name("fish")["id"]
    db_engine.insert_attendance("test1", create_id, "test")
    attendance_id = db_engine.get_attendance_by_title("test1")["id"]

    img_path = "/home/fish/PycharmProjects/Web&FaceRecognize/upload_image"
    for x in os.listdir(img_path):
        name = x.split('.')[0]
        data = open(os.path.join(img_path, x), 'rb').read()
        print(name, data[:20])
        feature, bbox = face_engine.recognize(data)
        db_engine.insert_attendance_user(name, os.path.join(img_path, x), feature, attendance_id)


if __name__ == '__main__':
    fake_data(DatabaseEngine())
