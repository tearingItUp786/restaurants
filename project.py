from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
import view_forms as vf
import random
import string
# creates flow object from client secret json file
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
# http client library
import httplib2
# convert in memory objects to json
import json
# turn stuff into responses we can send out
from flask import make_response
# similar to urlib2 but with improvements
import requests
import database_functions as db
import os

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())[
    'web']['client_id']


@app.route("/login")
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # pass the state in as a keyword argument so template can pass it to
    # gconnect
    return render_template("login.html", STATE=state)


@app.route("/gconnect", methods=['POST'])
def gconnect():
    # check to see if the argument passed in from the request matches server
    # state
    if request.args.get('state') != login_session['state']:
        # make_response converts strings into a valid response
        response = make_response(json.dumps("invalid parameteres", 401))
        response.headers['Content/type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        # the one time code I will be sending to google to veriy
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check if access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    #  If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    # login_session['access_token'] = credentials.access_token
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = db.getUserId(login_session['email'])
    # if user does not exist, user_id will be None
    if user_id is None:
        user_id = db.createUser(login_session=login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    print credentials.to_json()
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    print 'In gdisconnect access token is %s' % credentials.access_token
    print 'User name is: '
    print login_session['username']
    if credentials is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        # del login_session['access_token']
        login_session.pop('gplus_id', None)
        login_session.pop('username', None)
        login_session.pop('email', None)
        login_session.pop('picture', None)
        login_session.pop('user_id', None)
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route("/")
def restaurants():
    if 'username' not in login_session:
        restaurants = db.getAllRestaurants()
        return render_template("public_restaurants.html", restaurants=restaurants)
    if 'username' in login_session:
        restaurants = db.getAllRestaurants()
        return render_template("public_restaurants.html", restaurants=restaurants)


@app.route("/new", methods=['GET', 'POST'])
def add_restaurant():
    if "username" not in login_session:
        return redirect("/login")

    form = vf.NewRestaurantForm(request.form)
    if request.method == 'POST' and form.validate():
        addition = db.addRestaurantToDb(
            name=form.name.data, description=form.description.data, user_id=login_session['user_id'])
        if addition is None:
            flash("Restaurant with name %s already exists" % form.name.data)
        else:
            flash('Succesfully added %s' % form.name.data)
            return redirect(url_for('restaurants'))

    return render_template('new_restaurant.html', form=form)


@app.route("/edit/restaurant/<int:restaurant_id>", methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    if "username" not in login_session:
        return redirect("/login")

    form = vf.NewRestaurantForm(request.form)
    restaurant = db.getRestaurantById(restaurant_id)

    if request.method == 'POST' and form.validate():
        old_name = restaurant.name
        if db.editRestaurantFromDb(restaurant_id=restaurant_id, user_id=login_session['user_id'], name=form.name.data, description=form.description.data):
            if old_name == restaurant.name:
                flash("Succesfully edited %s" % old_name)
            else:
                flash("Succesfully edited %s to %s" %
                      (old_name, form.name.data))
            return redirect(url_for('restaurants'))
        else:
            flash("Don't try and pull a fast one buddy")
            return redirect(url_for('edit_restaurant', restaurant_id=restaurant_id))

    elif request.method == 'GET':
        if restaurant:
            form.name.data = restaurant.name
            form.description.data = restaurant.description
        else:
            return redirect(url_for('restaurants'))

    return render_template('edit_restaurant.html', restaurant=restaurant, form=form)


@app.route("/delete/restaurant/<int:restaurant_id>", methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    if "username" not in login_session:
        return redirect("/login")

    if request.method == 'POST':
        restaurant = db.getRestaurantById(restaurant_id)
        if db.deleteRestaurantFromDb(restaurant_id, login_session['user_id']):
            flash('Successfuly deleted %s' % restaurant.name)
            return redirect(url_for('restaurants'))

    if request.method == 'GET':
        restaurant = db.getRestaurantById(restaurant_id)
        if restaurant:
            return render_template("delete_restaurant.html", restaurant=restaurant)
        else:
            return redirect(url_for('restaurants'))


@app.route("/menu/<int:restaurant_id>")
def menu(restaurant_id):
    error = None
    if "username" not in login_session:
        return redirect("/login")

    menu_items = db.getAllMenuItems(restaurant_id)
    restaurant = db.getRestaurantById(restaurant_id)
    if restaurant:
        return render_template("restaurant_menu.html", restaurant=restaurant, menu_items=menu_items, error=error)
    else:
        return redirect(url_for('restaurants'))


@app.route("/menu/<int:restaurant_id>/new", methods=['GET', 'POST'])
def add_menu_item(restaurant_id):
    if "username" not in login_session:
        return redirect("/login")
    form = vf.MenuItemForm(request.form)
    print form.courses
    print form.name
    if request.method == 'POST' and form.validate():
        if db.addMenuItem(name=form.name.data, description=form.description.data, price=form.price.data, course=form.courses.data, restaurant_id=restaurant_id, user_id=login_session['user_id']):
            flash('Successfully added menu item %s' % form.name.data)
            return redirect(url_for('menu', restaurant_id=restaurant_id))
        else:
            flash("Menu item with name: %s already exists" % form.name.data)
            return render_template("new_menu_item.html", form=form)

    return render_template("new_menu_item.html", form=form)


@app.route("/menu/<int:restaurant_id>/edit", methods=['GET', 'POST'])
def edit_menu_items(restaurant_id):
    if "username" not in login_session:
        return redirect("/login")

    menu_items = db.getAllMenuItems(restaurant_id)
    if not menu_items:
        return redirect(url_for('menu', restaurant_id=restaurant_id))

    form = vf.UpdateMenuItemsForm(request.form)

    if request.method == 'GET':
        for item in menu_items:
            form_item = vf.MenuItemForm()
            form_item.name = item.name
            form_item.description = item.description
            form_item.price = item.price
            form_item.courses = item.course
            form_item.entry_id = item.id
            form.items.append_entry(form_item)
        return render_template('edit_menu_items.html', form=form)

    if request.method == 'POST':
        if form.validate():
            for item in form.items.data:
                if db.editMenuItem(item_id=item.get('entry_id'),
                                   user_id=login_session['user_id'],
                                   name=item.get('name'),
                                   description=item.get('description'),
                                   price=item.get('price'),
                                   course=item.get('courses'),
                                   restaurant_id=restaurant_id):
                    flash("Successfully updated menu item: %s" %
                          item.get('name'))
                else:
                    flash("Don't try and pull a fast one on me bruh")
                    return redirect(url_for('edit_menu_items', restaurant_id=restaurant_id))
            return redirect(url_for('menu', restaurant_id=restaurant_id))
        return render_template('edit_menu_items.html', form=form)


@app.route("/menu/<int:restaurant_id>/delete")
def delete_menu_item(restaurant_id):
    if "username" not in login_session:
        return redirect("/login")
    menu_items = db.getAllMenuItems(restaurant_id)
    if not menu_items:
        return redirect(url_for('menu', restaurant_id=restaurant_id))
    form = vf.DeleteMenuItemsForm(request.form)
    if request.method == 'GET':
        for item in menu_items:
            form_item = vf.MenuItemForm()
            form_item.name = item.name
            form_item.description = item.description
            form_item.price = item.price
            form_item.courses = item.course
            form_item.entry_id = item.id
            form.items.append_entry(form_item)
        return render_template('delete_menu_items.html', form=form)
    pass

if __name__ == "__main__":
    # need a secret key to access login_session
    app.secret_key = os.urandom(24)
    # this will make it reload upon saved changes
    app.debug = True
    # forward to the port
    app.run(host='0.0.0.0', port=5000)
