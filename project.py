from flask import Flask
app = Flask(__name__)


@app.route("/")
def restaurants():
    return "Main Page"


@app.route("/login")
def login():
    return "Login page"


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
    # this will make it reload upon saved changes
    app.debug = True
    # forward to the port
    app.run(host='0.0.0.0', port=5000)
