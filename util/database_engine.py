from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
