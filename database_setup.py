from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

course_enums = ('Appetizer', 'Entree', 'Dessert', 'Beverage')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    restaurants = relationship("Restaurant", cascade="all")


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", cascade="all")
    items = relationship("MenuItem", cascade="all")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date,
        }


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(Float(5, 2))
    course = Column(Enum(*course_enums))
    restaurant = relationship("Restaurant")
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    user = relationship("User")
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }

engine = create_engine('sqlite:///restaurants.db')
Base.metadata.create_all(engine)
