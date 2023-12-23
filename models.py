from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class First(Base):
    __tablename__ = 'shop_first'
    id = Column(Integer, Sequence('shop_first_id_seq'), primary_key=True)
    name = Column(String)
    type = Column(String)
    address = Column(String)
    round = Column(Integer)
    retailer_id = Column(String)

    @staticmethod
    def insert(data):
        session = Session()
        for item in data:
            record = First(name=item['name'], type=item['type'], address=item['address'], round=item['round'], retailer_id=item['retailer_id'])
            session.add(record)
        session.commit()


class Second(Base):
    __tablename__ = 'shop_second'
    id = Column(Integer, Sequence('shop_second_id_seq'), primary_key=True)
    name = Column(String)
    address = Column(String)
    round = Column(Integer)
    retailer_id = Column(String)

    @staticmethod
    def insert(data):
        session = Session()
        for item in data:
            record = Second(name=item['name'], address=item['address'], round=item['round'], retailer_id=item['retailer_id'])
            session.add(record)
        session.commit()

Base.metadata.create_all(engine)
