#!/usr/bin/env python3

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# class is a table in db
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="category")

    @property
    def serialize(self):

            return {
                'name': self.name,
                'id': self.id,
            }


class CategoryItem(Base):
    __tablename__ = 'category_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(
        Category,
        backref='category_item'
    )
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="category_item")
    # We added this serialize function to be able to send JSON objects in a
    # serializable format

    @property
    def serialize(self):

            return {
                'name': self.name,
                'description': self.description,
                'id': self.id,
            }

engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
