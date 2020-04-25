from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class ManageUser(Base):
    __tablename__ = 'manage_users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(20), nullable=False)

    def __repr__(self):
        return "<User(id='%s', username='%s', password='%s')>" \
               % (self.id, self.username, self.password)


class AttendanceUser(Base):
    __tablename__ = 'attendance_user'

    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    attendance_id = Column(Integer, nullable=False)
    feature_id = Column(Integer, nullable=False)


class AttendanceRecord(Base):
    __tablename__ = 'attendance_record'

    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    feature_id = Column(Integer, nullable=False)


class AttendanceDate(Base):
    __tablename__ = 'attendance_date'

    id = Column(Integer, primary_key=True)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    attendance_id = Column(Integer, nullable=False)


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
    src_path = Column(String(500), nullable=False)


class Feature(Base):
    __tablename__ = 'feature'

    id = Column(Integer, primary_key=True)
    data = Column(LargeBinary, nullable=False)


class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('manage_users.id'))
    title = Column(String(200), nullable=False)
    type = Column(Integer, nullable=False)
    info = Column(String(500))

    creator_user = relationship("ManageUser", back_populates="attendance")


if __name__ == '__main__':
    username = 'root'
    password = '109412'
    host = '127.0.0.1'
    port = 3306
    db = 'face'

    connect_str = 'mysql+mysqldb://{}:{}@{}:{}/{}' \
        .format(username, password, host, port, db)

    engine = create_engine(connect_str, echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    ed_user = ManageUser(username='fish', password='123456')
    print(ed_user)

    Session = sessionmaker()
    Session.configure(bind=engine)

    session = Session()

    session.add_all([
        ed_user,
        ManageUser(username="cat", password="123456"),
        ManageUser(username="A", password="123456"),
        ManageUser(username="B", password="123456")
    ])

    print(session.new)
    session.commit()
