from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class First(Base):
    __tablename__ = 'first_place'
    id = Column(Integer, Sequence('first_id_seq'), primary_key=True)
    name = Column(String)
    type = Column(String)
    address = Column(String)
    round = Column(Integer)

    @staticmethod
    def insert(data):
        session = Session()
        for item in data:
            record = First(name=item['name'], type=item['type'], address=item['address'], round=item['round'])
            session.add(record)
        session.commit()


class Second(Base):
    __tablename__ = 'second_place'
    id = Column(Integer, Sequence('second_id_seq'), primary_key=True)
    name = Column(String)
    address = Column(String)
    round = Column(Integer)

    @staticmethod
    def insert(data):
        session = Session()
        for item in data:
            record = Second(name=item['name'], address=item['address'], round=item['round'])
            session.add(record)
        session.commit()