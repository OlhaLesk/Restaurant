from sqlalchemy import Column, create_engine, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    description = Column(String(300), nullable=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'name': self.name,
                'id': self.id,
                'description': self.description}


class MenuItem(Base):
    __tablename__ = 'menu_item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    @property
    def serialize(self):
        return {'name': self.name,
                'description': self.description,
                'id': self.id,
                'price': self.price,
                'course': self.course,
        }

