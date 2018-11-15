#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database_setup import *

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Delete Categories if exisitng.
session.query(Category).delete()
# Delete CategoryItem if exisitng.
session.query(CategoryItem).delete()
# Delete Users if exisitng.
session.query(User).delete()

# Create fake users
User1 = User(
    name="Nada Baynom",
    email="nbaynom0@skype.com",
    picture='http://dummyimage.com/200x200.png/ff4444/ffffff'
)
session.add(User1)
session.commit()

User2 = User(
    name="Renado Gress",
    email="rgress1@t.co",
    picture='http://dummyimage.com/200x200.png/cc0000/ffffff'
)
session.add(User2)
session.commit()

User3 = User(
    name="Prinz Blakemore",
    email="pblakemore2@bluehost.com",
    picture='http://dummyimage.com/200x200.png/5fa2dd/ffffff'
)
session.add(User3)
session.commit()

# Create fake categories
Category1 = Category(name="Football", user_id=1)
session.add(Category1)
session.commit()

Category2 = Category(name="Cars", user_id=2)
session.add(Category2)
session.commit

Category3 = Category(name="Snacks", user_id=1)
session.add(Category3)
session.commit()

Category4 = Category(name="Gadgets", user_id=1)
session.add(Category4)
session.commit()

Category5 = Category(name="Food", user_id=1)
session.add(Category5)
session.commit()

Item1 = CategoryItem(
    name="Football Boots",
    description="Shoes to play football in.",
    category_id=1, user_id=1
)
session.add(Item1)
session.commit()

Item2 = CategoryItem(
    name="Football Shirt",
    description="Shirt to play football in.",
    category_id=1, user_id=1
)
session.add(Item2)
session.commit()

Item3 = CategoryItem(
    name="Football",
    description="A Football.",
    category_id=1, user_id=1
)
session.add(Item3)
session.commit()

Item4 = CategoryItem(name="BMW", description="car", category_id=2, user_id=2)
session.add(Item4)
session.commit()

print ("Your database has been populated with fake data!")