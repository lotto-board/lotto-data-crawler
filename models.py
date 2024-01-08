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
            record = First(
                name=item['name'],
                type=item['type'],
                address=item['address'],
                round=item['round'],
                retailer_id=item['retailer_id']
            )
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
            record = Second(
                name=item['name'],
                address=item['address'],
                round=item['round'],
                retailer_id=item['retailer_id']
            )
            session.add(record)
        session.commit()


class ShopInfo(Base):
    __tablename__ = 'shop_info'
    retailer_id = Column(String, primary_key=True)
    address = Column(String)
    name = Column(String)
    phone_number = Column(String)
    latitude = Column(String)
    longitude = Column(String)

    @staticmethod
    def select_all_id(session):
        return session.query(ShopInfo.retailer_id).all()
    
    @staticmethod
    def select_all_if_null(session):
        return session.query(ShopInfo.retailer_id).filter(ShopInfo.address.is_(None)).all()
    
    @staticmethod
    def select_all_address(session):
        return session.query(ShopInfo).all()

    @staticmethod
    def update(session, retailer_id, data):
        record = session.query(ShopInfo).get(retailer_id)
        if record:
            record.name = data['name']
            record.address = data['address']
            record.phone_number = data['phone_number']
            record.longitude = data['longitude']
            record.latitude = data['latitude']
            session.add(record)

    @staticmethod
    def is_exist(session, retailer_id):
        return session.query(ShopInfo).filter(ShopInfo.retailer_id == retailer_id).first() is not None

    @staticmethod
    def insert(session, data):
        new_shop = ShopInfo(
            retailer_id=data['retailer_id'],
            name=data['name'],
            address=data['address'],
            phone_number=data['phone_number'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        session.add(new_shop)


class WinningShop(Base):
    __tablename__ = 'winning_shop'
    retailer_id = Column(String, primary_key=True)
    count_shop_first = Column(Integer)
    count_shop_second = Column(Integer)

    @staticmethod
    def upsert_record(session, retailer_id, is_first):
        record = session.query(WinningShop).filter(WinningShop.retailer_id == retailer_id).first()

        if record is None:
            record = WinningShop(
                retailer_id=retailer_id,
                count_shop_first=0,
                count_shop_second=0
            )
        print(f"Upsert record: {record.retailer_id}, firstCount: {record.count_shop_first}, secondCount: {record.count_shop_second}")

        if is_first:
            record.count_shop_first = record.count_shop_first + 1
        else:
            record.count_shop_second = record.count_shop_second + 1

        session.add(record)


Base.metadata.create_all(engine)
