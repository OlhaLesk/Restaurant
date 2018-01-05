from configparser import ConfigParser
from flask import (flash,
                   Flask,
                   jsonify,
                   redirect,
                   render_template,
                   request,
                   url_for)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


config = ConfigParser()
config.read('config.ini')
HOST = config['MYSQL']['host']
USERNAME = config['MYSQL']['username']
PASSWORD = config['MYSQL']['password']
DB = config['MYSQL']['name']

app = Flask(__name__)
engine = create_engine('mysql://%s:%s@%s/%s' % (USERNAME, PASSWORD, HOST, DB))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'],
                                    description=request.form['description'])
        session.add(new_restaurant)
        session.commit()
        flash("A new restaurant is created!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    edited_restaurant = session.query(Restaurant).filter_by(id=restaurant_id) \
                                                 .one()
    if request.method == 'POST':
        if request.form['name']:
            edited_restaurant.name = request.form['name']
            session.add(edited_restaurant)
            session.commit()
            flash("Restaurant has been edited")
            return redirect(url_for('showRestaurants'))
        if request.form['description']:
            edited_restaurant.description = request.form['description']
            session.add(edited_restaurant)
            session.commit()
            flash("Restaurant has been edited")
            return redirect(url_for('showRestaurants'))
    else:
        return render_template(
            'editrestaurant.html', restaurant_id=restaurant_id,
            restaurant=edited_restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
     restaurant_to_delete = session.query(Restaurant) \
                                   .filter_by(id=restaurant_id).one()
     if request.method == 'POST':
         session.delete(restaurant_to_delete)
         session.commit()
         flash("Restaurant has been deleted")
         return redirect(url_for('showRestaurants'))
     else:
         return render_template('deleterestaurant.html',
                                restaurant=restaurant_to_delete)

@app.route('/restaurants/JSON')
def showRestaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[restaurant.serialize
                                for restaurant in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

# JSON ENDPOINT
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=menu_item.serialize)

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'],
                            description=request.form['description'],
                            price=request.form['price'],
                            course=request.form['course'],
                            restaurant_id=restaurant_id)
        session.add(new_item)
        session.commit()
        flash("A new menu item is created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    edited_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        session.add(edited_item)
        session.commit()
        flash("Menu Item has been edited")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               item=edited_item)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    item_to_delete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash("Menu Item has been deleted")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteconfirmation.html', item=item_to_delete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
