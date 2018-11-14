#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from sqlalchemy.pool import SingletonThreadPool, NullPool,StaticPool

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from login_decorator import login_required

app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item-catalog-Application"

engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread':False},poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print(request.args.get('state'))
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print('accesssss  ',access_token)
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id=getUserID(login_session['email'])
    if not user_id:
        user_id=createUser(login_session)
    login_session['user_id'] = user_id
    

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


@app.route('/localLogin', methods=['POST'])
def localAuthorize():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    email=request.form['email']
    user_id=getUserID(email)
    if not user_id:
        user_id=createUser(login_session)
    login_session['user_id'] = user_id
    login_session['username'] =request.form['userName'] 

    return redirect(url_for('catalog'))



# User Helper Functions
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


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print( 'In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('catalog'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

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
    # del login_session['access_token']
    # del login_session['gplus_id']
    # del login_session['username']
    # del login_session['email']
    # del login_session['picture']
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
    category=session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session or item.user_id != login_session['user_id']:
        return render_template('publicCatalogItem.html', item=item,category_id=category_id)    
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template('catalogitem.html', item=item,category_id=category_id) 
   

#Add new item
@app.route('/catalog/items/new',methods=['GET', 'POST'])
@login_required
def newItem():
    
    if request.method == 'POST':
        selectedCategory=request.form['category']
        category=session.query(Category).filter_by(name=selectedCategory).one()
        user_id=login_session['user_id']
        newItem = CategoryItem(
            name=request.form['name'], category_id=category.id,description=request.form['description'],user_id=user_id)
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

# disconnect from the login session
@app.route('/disconnect')
def disconnect():
    if 'username' in login_session:
        gdisconnect()
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', port=9874)