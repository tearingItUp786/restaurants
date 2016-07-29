from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databasesetup import Base, User, Restaurant, MenuItem
from flask import flash


engine = create_engine('sqlite:///restaurants.db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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


def getAllRestaurants():
    return session.query(Restaurant).all()


def getRestaurantByName(name):
    restaurant = session.query(Restaurant).filter_by(name=name).first()
    if restaurant:
        return restaurant
    else:
        return None


def getRestaurantById(id):
    restaurant = session.query(Restaurant).filter_by(id=id).first()
    if restaurant:
        return restaurant
    else:
        return None


def addRestaurantToDb(name, description, user_id):
    if getRestaurantByName(name=name) is None:
        aRestaurant = Restaurant(
            name=name, description=description, user_id=user_id)
        session.add(aRestaurant)
        flash('Successfuly added %s' % name)
        session.commit()
        return True
    else:
        flash("%s already exists" % name)
        return None


def deleteRestaurantFromDb(restaurant_id, user_id):
    restaurant = getRestaurantById(restaurant_id)
    if user_id == restaurant.user_id:
        session.delete(restaurant)
        flash("%s successfully deleted" % restaurant.name)
        session.commit()
    else:
        user = getUserInfo(user_id)
        flash("%s is not the owner of this restaurant" % user.name)


def editRestaurantFromDb(restaurant_id, user_id, name, description):
    editedRestaurant = getRestaurantById(restaurant_id)
    old_restaurant_name = editedRestaurant.name
    if user_id == editedRestaurant.user_id:
        if name:
            editedRestaurant.name = name
        if description:
            editedRestaurant.description = description
        flash("%s succesfully edited and is now %s" % (old_restaurant_name, editedRestaurant.name))
        session.add(editedRestaurant)
        session.commit()


def addMenuItem(name, description, price, course, restaurant_id, user_id):
    menuItem = MenuItem(name=name, description=description, price=price,
                        course=course, restaurant_id=restaurant_id, user_id=user_id)
    session.add(menuItem)
    session.commit()
