import datetime
import os
import time

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from face.face_engine import FaceEngine
from util.database_model import Base, AttendanceUser, Attendance, ManageUser, Photo, Feature, AttendanceRecord, \
    AttendanceDate
from util.common_tools import bin_to_array, array_to_bin, generator_random_code
from util.fish_logger import log


class DatabaseEngine:
    def __init__(self, args=None):
        if args is None:
            args = self.get_simple_args()

        connect_str = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8' \
            .format(args['username'], args['password'], args['host'], args['port'], args['db'])

        self.engine = create_engine(connect_str, echo=False, pool_size=100)
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
                'feature': bin_to_array(user.feature.data)
            })
        session.close()
        return rst

    def get_user_by_name(self, username):
        session = self.Session()
        for user in session.query(ManageUser).filter_by(username=username):
            rst = {
                "id": user.id,
                "username": user.username,
                "password": user.password,
                "type": user.type
            }
            session.close()
            return rst
        session.close()
        return None

    def update_attendance(self, _id, title, info, _type):
        session = self.Session()
        obj = session.query(Attendance).filter_by(id=_id).one()
        obj.title = title
        obj.info = info
        obj.type = _type
        session.commit()
        session.close()
        return True

    def update_attendance_code(self, _id):
        session = self.Session()
        obj = session.query(Attendance).filter_by(id=_id).one()
        obj.code = generator_random_code(16)
        session.commit()
        session.close()
        return True

    def delete_attendance(self, _id):
        session = self.Session()
        obj = session.query(Attendance).filter_by(id=_id).one()
        session.delete(obj)
        session.commit()
        session.close()
        return True

    def get_attendance_by_index(self, title_prefix, creator, offset, limit):
        session = self.Session()
        res = []

        count = session.query(Attendance).join(ManageUser, Attendance.creator_id == ManageUser.id). \
            filter(Attendance.title.like("{}%".format(title_prefix))). \
            filter(ManageUser.username.like("{}%".format(creator))).count()

        for item in session.query(Attendance).join(ManageUser, Attendance.creator_id == ManageUser.id). \
                filter(Attendance.title.like("{}%".format(title_prefix))). \
                filter(ManageUser.username.like("{}%".format(creator))). \
                offset(offset). \
                limit(limit):
            res.append({
                "id": item.id,
                "creator": item.creator_user.username,
                "title": item.title,
                "type": item.type,
                "info": item.info,
                "code": item.code
            })
        session.close()
        return res, count

    def check_attendance(self, attendance_id, code):
        session = self.Session()

        ok = False
        if session.query(Attendance).filter_by(id=attendance_id, code=code).count() == 1:
            ok = True

        session.close()
        return ok

    def get_attendance_user_by_index(self, name_prefix, attendance_title, offset, limit):
        session = self.Session()
        res = []

        count = session.query(AttendanceUser).join(Attendance, AttendanceUser.attendance_id == Attendance.id). \
            filter(Attendance.title.like("{}%".format(attendance_title))). \
            filter(AttendanceUser.name.like("{}%".format(name_prefix))).count()

        for item in session.query(AttendanceUser).join(Attendance, AttendanceUser.attendance_id == Attendance.id). \
                filter(Attendance.title.like("{}%".format(attendance_title))). \
                filter(AttendanceUser.name.like("{}%".format(name_prefix))). \
                offset(offset). \
                limit(limit):
            res.append({
                "id": item.id,
                "name": item.name,
                "photo": item.photo.src_path,
                "attendance_title": item.attendance.title
            })
        session.close()
        return res, count

    def update_attendance_user(self, _id, name):
        session = self.Session()
        obj = session.query(AttendanceUser).filter_by(id=_id).one()
        obj.name = name
        session.commit()
        session.close()
        return True

    def delete_attendance_user(self, _id):
        session = self.Session()
        obj = session.query(AttendanceUser).filter_by(id=_id).one()
        session.delete(obj)
        session.commit()
        session.close()
        return True

    def get_record_by_index(self, name_prefix, attendance_title, offset, limit):
        session = self.Session()
        res = []

        count = session.query(AttendanceRecord).join(Attendance, AttendanceRecord.attendance_id == Attendance.id). \
            join(AttendanceUser, AttendanceRecord.user_id == AttendanceUser.id). \
            filter(Attendance.title.like("{}%".format(attendance_title))). \
            filter(AttendanceUser.name.like("{}%".format(name_prefix))).count()

        for item in session.query(AttendanceRecord).join(Attendance, AttendanceRecord.attendance_id == Attendance.id). \
                join(AttendanceUser, AttendanceRecord.user_id == AttendanceUser.id). \
                filter(Attendance.title.like("{}%".format(attendance_title))). \
                filter(AttendanceUser.name.like("{}%".format(name_prefix))). \
                offset(offset). \
                limit(limit):
            res.append({
                "id": item.id,
                "name": item.user.name,
                "photo": item.photo.src_path,
                "attendance_title": item.attendance.title,
                "date": item.date
            })
        session.close()

        log.info('{} {}'.format(count, len(res)))

        return res, count

    def get_today_attendance_num(self):
        session = self.Session()

        rst = [0] * 24

        now = datetime.datetime.now()

        for hour in range(24):
            st_time = datetime.datetime(now.year, now.month, now.day, hour).timestamp()
            en_time = datetime.datetime(now.year, now.month, now.day, hour, 59, 59).timestamp()

            rst[hour] = session.query(AttendanceRecord). \
                join(Attendance, AttendanceRecord.attendance_id == Attendance.id). \
                join(AttendanceUser, AttendanceRecord.user_id == AttendanceUser.id). \
                filter(st_time <= AttendanceRecord.date). \
                filter(AttendanceRecord.date <= en_time). \
                order_by(desc(AttendanceRecord.date)).count()

        return rst

    def get_last_7days_attendance_num(self):
        session = self.Session()

        rst = []

        now = datetime.datetime.now()

        for days in list(range(7))[::-1]:
            day_delta = datetime.timedelta(days=1)

            st_time = (datetime.datetime(now.year, now.month, now.day) - day_delta * days).timestamp()
            en_time = (datetime.datetime(now.year, now.month, now.day, 23, 59, 59) - day_delta * days).timestamp()

            num = session.query(AttendanceRecord). \
                join(Attendance, AttendanceRecord.attendance_id == Attendance.id). \
                join(AttendanceUser, AttendanceRecord.user_id == AttendanceUser.id). \
                filter(st_time <= AttendanceRecord.date). \
                filter(AttendanceRecord.date <= en_time). \
                order_by(desc(AttendanceRecord.date)).count()

            rst.append(num)

        print(rst)

        return rst

    def get_recent_record(self, limit=8):
        session = self.Session()
        res = []

        for item in session.query(AttendanceRecord).join(Attendance, AttendanceRecord.attendance_id == Attendance.id). \
                join(AttendanceUser, AttendanceRecord.user_id == AttendanceUser.id). \
                order_by(desc(AttendanceRecord.date)). \
                limit(limit):
            res.append({
                "id": item.id,
                "name": item.user.name,
                "photo": item.photo.src_path,
                "attendance_title": item.attendance.title,
                "date": item.date
            })
        session.close()

        return res

    def delete_record(self, _id):
        session = self.Session()
        obj = session.query(AttendanceRecord).filter_by(id=_id).one()
        session.delete(obj)
        session.commit()
        session.close()
        return True

    def get_attendance_by_title(self, title):
        session = self.Session()
        for item in session.query(Attendance).filter_by(title=title):
            rst = {
                "id": item.id,
                "creator": item.creator_user.username,
                "title": item.title,
                "type": item.type,
                "info": item.info
            }
            session.close()
            return rst
        session.close()
        return None

    def insert_attendance(self, title, create_id=None, info=None, _type=1):
        item = Attendance()
        item.title = title
        item.creator_id = create_id
        item.info = info
        item.type = _type
        item.code = generator_random_code(16)

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

    def check_record(self, attendance_id, user_id):
        session = self.Session()

        now = datetime.datetime.now()
        tnow = now.hour * 60 * 60 + now.minute * 60 + now.second

        attendance = session.query(Attendance).filter_by(id=attendance_id).one()

        print('{} asdasd {}'.format(now.weekday() + 1, attendance.week_list))

        if str(now.weekday() + 1) not in attendance.week_list:
            return None

        user = session.query(AttendanceUser).filter_by(id=user_id).one()

        if len(user.record_list) > 0:
            last_date = None
            last_time = None
            for item in user.record_list:
                if item.attendance_date is None:
                    continue
                if last_time is None or last_time < item.date:
                    last_date = item.attendance_date
                    last_time = item.date

            if last_date is not None:
                last = datetime.datetime.fromtimestamp(last_time)
                bound = datetime.datetime(last.year, last.month, last.day,
                                          last_date.end_time // 3600,
                                          last_date.end_time // 60 % 60,
                                          last_date.end_time % 60)

                if int(bound.timestamp()) >= int(now.timestamp()):
                    log.info('bound: {}, now: {}'.format(bound, now))
                    session.close()
                    return None

        for date in attendance.date_list:
            log.info(" {} {} {} ".format(date.start_time, date.end_time, tnow))
            if date.start_time <= tnow <= date.end_time:
                session.close()
                return date.id

        session.close()

    def insert_record(self, user_id, attendance_id, photo_src, feature_array, attendance_date_id):

        photo = Photo()
        photo.src_path = photo_src

        feature = Feature()
        feature.photo = photo
        feature.data = array_to_bin(feature_array)

        item = AttendanceRecord()
        item.attendance_id = attendance_id
        item.user_id = user_id
        item.photo = photo
        item.feature = feature
        item.date = int(time.time())
        item.attendance_date_id = attendance_date_id

        session = self.Session()
        session.add(item)
        session.commit()
        session.close()

    def upload_attendance_date(self, date_list, attendance_id, week_list=None):
        if week_list is None:
            week_list = [1, 2, 3, 4, 5]

        session = self.Session()

        week_str = ''
        for x in week_list:
            week_str += str(x)

        session.query(Attendance).filter_by(id=attendance_id).one().week_list = week_str

        for date in session.query(Attendance).filter_by(id=attendance_id).one().date_list:
            session.delete(date)

        for date in date_list:
            item = AttendanceDate()
            item.attendance_id = attendance_id
            item.start_time = date[0]
            item.end_time = date[1]
            session.add(item)

        session.commit()
        session.close()

    def get_attendance_date(self, attendance_id):
        session = self.Session()

        time_list = []
        week_list = []

        attendance = session.query(Attendance).filter_by(id=attendance_id).one()

        for date in attendance.date_list:
            session.delete(date)
            time_list.append([date.start_time, date.end_time])

        for x in attendance.week_list:
            week_list.append(int(x))

        return time_list, week_list

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

    def get_manager_user_by_index(self, name_prefix, offset, limit):
        session = self.Session()
        res = []

        count = session.query(ManageUser).\
            filter(ManageUser.username.like("{}%".format(name_prefix))). \
            filter(ManageUser.username != 'root').count()

        for item in session.query(ManageUser). \
                filter(ManageUser.username.like("{}%".format(name_prefix))). \
                filter(ManageUser.username != 'root').\
                offset(offset). \
                limit(limit):
            res.append({
                "id": item.id,
                "username": item.username,
                "password": item.password
            })
        session.close()
        return res, count

    def update_manager_user(self, _id, username, password):
        session = self.Session()
        obj = session.query(ManageUser).filter_by(id=_id).one()
        obj.username = username
        obj.password = password
        session.commit()
        session.close()
        return True

    def delete_manager_user(self, _id):
        session = self.Session()
        obj = session.query(ManageUser).filter_by(id=_id).one()
        session.delete(obj)
        session.commit()
        session.close()
        return True


def fake_data(db_engine):
    face_engine = FaceEngine()
    db_engine.init_db()
    db_engine.insert_manager_user("fish", "123456")
    create_id = db_engine.get_user_by_name("fish")["id"]
    db_engine.insert_attendance("test1", create_id, "test")
    for x in range(2, 100):
        db_engine.insert_attendance("test" + str(x), create_id, "test")
    attendance_id = db_engine.get_attendance_by_title("test1")["id"]
    db_engine.upload_attendance_date([[0, 23 * 3600 + 59 * 60 + 59]], 1)

    img_path = "../images/upload_image"
    img_path = os.path.abspath(img_path)
    for x in os.listdir(img_path):
        name = x.split('.')[0]
        data = open(os.path.join(img_path, x), 'rb').read()
        print(name, data[:20])

        feature, bbox = face_engine.recognize(data)
        db_engine.insert_attendance_user(name, os.path.join(img_path, x), feature, attendance_id)
        db_engine.insert_record(1, 1, os.path.join(img_path, x), feature, 1)


def test(db_engine):
    print(db_engine.get_retrieve_user(1))


if __name__ == '__main__':
    fake_data(DatabaseEngine())
    # t = DatabaseEngine()
    # t.init_db()
    # t = DatabaseEngine()
    # session = t.Session()
    # for item in session.query(AttendanceRecord).join(Attendance).join(AttendanceUser). \
    #         filter(Attendance.title.like("{}%".format(""))). \
    #         filter(AttendanceUser.name.like("{}%".format(""))):
    #     print(item)
    #
    # d = session.query(AttendanceRecord). \
    #     join(Attendance, AttendanceRecord.attendance_id == Attendance.id). \
    #     join(AttendanceUser, AttendanceUser.id == AttendanceRecord.user_id). \
    #     filter(Attendance.title.like("{}%".format(""))). \
    #     filter(AttendanceUser.name.like("{}%".format(""))).count()
    #
    # print(d)
