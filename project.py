from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
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
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    print credentials.to_json()
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session[
        'access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route("/")
@app.route("/restaurant")
def restaurants():
    return "Main Page"


@app.route("/new restaurant")
def add_restaurant():
    return "Adding a new restaurant"


@app.route("/edit/restaurant/<int:restaurant_id>")
def edit_restaurant(restaurant_id):
    return "Editing %s" % (restaurant_id)


@app.route("/delete/restaurant/<int:restaurant_id>")
def delete_restaurant(restaurant_id):
    bro = "Taranveer Bains"
    return "Deleting %s %s" % (restaurant_id, bro)


@app.route("/menu/<int:restaurant_id>")
def menu(restaurant_id):
    return "Menu for %s" % restaurant_id


@app.route("/menu/<int:restaurant_id>/add")
def add_menu_item(restaurant_id):
    return "Adding item to %s" % restaurant_id


@app.route("/menu/<int:restaurant_id>/edit/<int:menu_id>")
def edit_menu_item(restaurant_id, menu_id):
    return "Editing %s" % menu_id


@app.route("/menu/<int:restaurant_id>/<int:menu_id>/delete")
def delete_menu_item(restaurant_id, menu_id):
    return "Deleting %s" % menu_id

if __name__ == "__main__":
    # need a secret key to access login_session
    app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                             for x in range(32))
    # this will make it reload upon saved changes
    app.debug = True
    # forward to the port
    app.run(host='0.0.0.0', port=5000)
