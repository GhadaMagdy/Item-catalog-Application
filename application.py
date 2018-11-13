#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from sqlalchemy.pool import SingletonThreadPool, NullPool,StaticPool

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread':False},poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def catalog():
    categories=session.query(Category).all()
    return render_template('catalog.html', categories=categories)


@app.route('/catalog/categories/<int:category_id>')
def catgoryItems(category_id):
    items=session.query(CategoryItem).filter_by(category_id=category_id)
    category=session.query(Category).filter_by(id=category_id).one()
    return render_template('catalogItems.html', items=items,category=category)    

@app.route('/catalog/categories/<int:category_id>/items/<int:item_id>')
def item(category_id,item_id):
    item=session.query(CategoryItem).filter_by(id=item_id).one()
    return render_template('catalogitem.html', item=item,category_id)    

@app.route('/catalog/items/new',methods=['GET', 'POST'])
def newItem():
    if request.method == 'POST':
        selectedCategory=request.form['category']
        category=session.query(Category).filter_by(name=selectedCategory).one()
        newItem = CategoryItem(
            name=request.form['name'], category_id=category.id,description=request.form['description'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('catgoryItems', category_id=category.id))
    else:
        categories=session.query(Category).all()
        return render_template('newItem.html', categories=categories)

@app.route('/catalog/categories/<int:category_id>/items/<int:item_id>/edit',methods=['GET', 'POST'])
def editItem(category_id,item_id):
    if request.method == 'POST':
        selectedCategory=request.form['category']
        category=session.query(Category).filter_by(name=selectedCategory).one()
        newItem = CategoryItem(
            name=request.form['name'], category_id=category.id,description=request.form['description'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('editItem', category_id=category_id,item_id=item_id))
    else:
        categories=session.query(Category).all()
        return render_template('newItem.html', categories=categories)


@app.route('/catalog/categories/<int:category_id>/items/<int:item_id>/delete')
def deleteItem(category_id,item_id):
    return 'item delete'

@app.route('/catalog/JSON')
def categoriesjson():
    return "categories in json"

@app.route('/catalog/categories/<int:category_id>/JSON')
def categoryItemsjson(category_id):
    return "items in category json"  

@app.route('/catalog/categories/<int:category_id>/items/<int:item_id>/JSON')
def categoryItemjson(category_id,item_id):
    return "item  json" 

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9874)