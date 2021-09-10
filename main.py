import os
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps, Map, get_coordinates

# set your google api via environ variable
api = os.environ['api']
app = Flask(__name__)
GoogleMaps(app, key=api)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean(), nullable=False, default=False, server_default="false")
    has_toilet = db.Column(db.Boolean(), nullable=False, default=False, server_default="false")
    has_wifi = db.Column(db.Boolean(), nullable=False, default=False, server_default="false")
    can_take_calls = db.Column(db.Boolean(), nullable=False, default=False, server_default="false")
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)


# get all coffees from DB
def get_all_coffees():
    return db.session.query(Cafe).all()


# return geo coordinates from cafe name
def get_coord_from_name(coffee_name):
    lat = (get_coordinates(api, coffee_name.name)["lat"])
    lng = (get_coordinates(api, coffee_name.name)["lng"])
    dmap = Map(
        identifier="dmap",
        varname="dmap",
        lat=lat,
        lng=lng,
        markers=[{
            'icon': 'https://maps.google.com/mapfiles/ms/icons/orange-dot.png',
            'lat': lat,
            'lng': lng,
            'infobox': coffee_name.name,
        }],
        style="height:50%;width:100%;margin:0;color:#242f3e;",
    )
    return dmap


# return bool value from checkboxes
def true_false(checkbox):
    if checkbox:
        return True
    else:
        return False


@app.route("/")
def home():
    return render_template("index.html", dmap=None)


@app.route("/all_coffees")
def all_coffees():
    coffees = get_all_coffees()
    # Geocoding: getting coordinates from address text
    markers = []
    # for item in coffees:
    #     markers.append(
    #         {
    #             'icon': 'https://maps.google.com/mapfiles/ms/icons/orange-dot.png',
    #             'lat': (get_coordinates(api, item.name)["lat"]),
    #             'lng': (get_coordinates(api, item.name)["lng"]),
    #             'infobox': item.name,
    #         }
    #     )

    dmap = Map(
        identifier="dmap",
        varname="dmap",
        lat=51.50578984618858,
        lng=-0.07115033329515573,
        # markers=markers,

        style="height:100%;width:100%;margin:0;color:#242f3e;",
    )
    return render_template("all_coffees.html", dmap=dmap, coffees=coffees)


@app.route("/<selected_coffee>")
def coffee_detail(selected_coffee):
    coffee = Cafe.query.filter_by(name=selected_coffee).first()
    coordinates = get_coord_from_name(coffee_name=coffee)
    return render_template("coffee.html", dmap=coordinates, coffee=coffee)


@app.route("/add_cafe", methods=['POST', 'GET'])
def add_cafe():
    if request.method == 'GET':
        return render_template("add_cafe.html", dmap=None)
    if request.method == 'POST':
        form_data = request.form
        new_coffee = Cafe(name=form_data["name"],
                          img_url=form_data["image_url"],
                          map_url=form_data["map_url"],
                          location=form_data["location"],
                          has_sockets=true_false(request.form.get("socket_checkbox")),
                          has_toilet=true_false(request.form.get("toilet_checkbox")),
                          has_wifi=true_false(request.form.get("wifi_checkbox")),
                          can_take_calls=true_false(request.form.get("calls_checkbox")),
                          seats=form_data["seats"],
                          coffee_price=f'£{form_data["price"]}',
                          )
        db.session.add(new_coffee)
        db.session.commit()
        return render_template("index.html", dmap=None)


@app.route("/delete/<selected_coffee>")
def delete(selected_coffee):
    coffee = Cafe.query.filter_by(name=selected_coffee).first()
    db.session.delete(coffee)
    db.session.commit()
    return render_template("index.html", dmap=None)


if __name__ == "__main__":
    app.run(debug=True)
