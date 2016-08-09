from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Restaurant, MenuItem, course_enums


engine = create_engine('sqlite:///restaurants.db')
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


def addRestaurantToDb(name, description, user_id):
    if getRestaurantByName(name=name) is None:
        aRestaurant = Restaurant(
            name=name, description=description, user_id=user_id)
        session.add(aRestaurant)
        session.commit()
        return True


def deleteRestaurantFromDb(restaurant_id, user_id):
    restaurant = getRestaurantById(restaurant_id)
    if user_id == restaurant.user_id:
        session.delete(restaurant)
        session.commit()
        return True


def editRestaurantFromDb(restaurant_id, user_id, name, description):
    editedRestaurant = getRestaurantById(restaurant_id)
    if user_id == editedRestaurant.user_id:
        if name:
            editedRestaurant.name = name
        if description:
            editedRestaurant.description = description
        session.add(editedRestaurant)
        session.commit()
        return True


def getAllMenuItems(restaurant_id):
    return session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()


def getMenuItemById(id):
    menuItem = session.query(MenuItem).filter_by(id=id).first()
    if menuItem:
        return menuItem


def getMenuItemByName(name, restaurant_id):
    menuItem = session.query(MenuItem).filter_by(name=name).first()
    if menuItem is not None:
        if menuItem.restaurant_id == restaurant_id:
            return menuItem
        else:
            return None
    else:
        return None


def getCourseEnumList():
    return course_enums


def addMenuItem(name, description, price, course, restaurant_id, user_id):
    menuItem = getMenuItemByName(name=name, restaurant_id=restaurant_id)
    if menuItem is None:
        menuItem = MenuItem(name=name, description=description, price=price,
                            course=course, restaurant_id=restaurant_id, user_id=user_id)
        session.add(menuItem)
        session.commit()
        return True


def editMenuItem(item_id, user_id, name, description, price, course, restaurant_id):
    editedMenuItem = getMenuItemById(item_id)
    duplicate = getMenuItemByName(name=name, restaurant_id=restaurant_id)
    if duplicate is not None:
        if editedMenuItem.name != duplicate.name:
            return False
    if editedMenuItem.user_id == user_id:
        if name:
            editedMenuItem.name = name
        if description:
            editedMenuItem.description = description
        if price:
            editedMenuItem.price = price
        if course:
            editMenuItem.course = course
        session.add(editedMenuItem)
        session.commit()
        return True
