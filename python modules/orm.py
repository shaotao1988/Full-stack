
import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

class MenuItem(Base):
    __tablename__ = 'menu_item'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(20), nullable = True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)


engine = create_engine('sqlite:///test.sqlite')

Base.metadata.create_all(engine)

if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    FirstRestarant = Restaurant(name = "Pizza Palace")
    session.add(FirstRestarant)
    session.commit()

    print(session.query(Restaurant).all())

    cheesepizza = MenuItem(name = "Cheese Pizza", description = "Made with all natural ingredients and fresh mozzarella", \
        course = "Entree", price = "$8.99", restaurant = FirstRestarant)
    session.add(cheesepizza)
    session.commit()
    print(session.query(MenuItem).all())
