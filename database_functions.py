from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databasesetup import Base, User, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurants.db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def add_restaurant_to_db(name, description, user_id):
    aRestaurant = Restaurant(
        name=name, description=description, user_id=user_id)
    session.add(aRestaurant)
    session.commit()


def search_for_a_restaurant(id):
    if session.query(Restaurant).filter_by(id=id).first():
        return session.query(Restaurant).filter_by(id=id).first()
