#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from sqlalchemy.pool import SingletonThreadPool, NullPool,StaticPool

from flask import session as login_session
import random
import string

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread':False},poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state)

#Get all gategories in cataloh
@app.route('/')
@app.route('/catalog/')
def catalog():
    categories=session.query(Category).all()
    return render_template('catalog.html', categories=categories)


#Get all items in specific category
@app.route('/catalog/categories/<int:category_id>')
def catgoryItems(category_id):
    items=session.query(CategoryItem).filter_by(category_id=category_id)
    category=session.query(Category).filter_by(id=category_id).one()
    return render_template('catalogItems.html', items=items,category=category)    

#Get item information
@app.route('/catalog/categories/<int:category_id>/items/<int:item_id>')
def item(category_id,item_id):
    item=session.query(CategoryItem).filter_by(id=item_id).one()
    return render_template('catalogitem.html', item=item,category_id=category_id)    

#Add new item
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

#Edit Item
@app.route('/catalog/categories/<int:category_id>/items/<int:item_id>/edit',methods=['GET', 'POST'])
def editItem(category_id,item_id):
    if request.method == 'POST':
        item=session.query(CategoryItem).filter_by(id=item_id).one()
        selectedCategory=request.form['category']
        category=session.query(Category).filter_by(name=selectedCategory).one()
        item.name=request.form['name']
        item.category_id=category.id
        item.description=request.form['description']
        session.add(item)
        session.commit()
        return redirect(url_for('item', category_id=category_id,item_id=item_id))
    else:
        categories=session.query(Category).all()
        item=session.query(CategoryItem).filter_by(id=item_id).one()
        return render_template('editCatalogItem.html', categories=categories,category_id=category_id,item=item)

#Delete Item
@app.route('/catalog/categories/<int:category_id>/items/<int:item_id>/delete',methods=['GET', 'POST'])
def deleteItem(category_id,item_id):
    if request.method == 'POST':
        item=session.query(CategoryItem).filter_by(id=item_id).one()
        session.delete(item)
        session.commit()
        return redirect(url_for('catgoryItems', category_id=category_id))
    else:
        item=session.query(CategoryItem).filter_by(id=item_id).one()
        return render_template('deleteCatalogItem.html',item=item,category_id=category_id)

#for public use
#get all gategories in JSON form
@app.route('/catalog/categories/JSON')
def catalogjson():
    categories=session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])

#get all items in specific category in JSON form
@app.route('/catalog/categories/<string:category_name>/items/JSON')
def categoryItemsjson(category_name):
    category=session.query(Category).filter_by(name=category_name).one()
    items=session.query(CategoryItem).filter_by(category_id=category.id)
    return jsonify(CategoryItems=[i.serialize for i in items]) 

#get item information in JSON form
@app.route('/catalog/categories/<string:category_name>/items/<string:item_name>/JSON')
def categoryItemjson(category_name,item_name):
    item=session.query(CategoryItem).filter_by(name=item_name).one()
    return jsonify(CategoryItem=[item.serialize])

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', port=9874)