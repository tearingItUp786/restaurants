from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databasesetup import Base, User, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurants.db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], image=login_session['image'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def addRestaurantToDb(name, description, user_id):
    aRestaurant = Restaurant(
        name=name, description=description, user_id=user_id)
    session.add(aRestaurant)
    session.commit()


def searchForRestaurant(id):
    if session.query(Restaurant).filter_by(id=id).first():
        return session.query(Restaurant).filter_by(id=id).first()
