import hmac
import sqlite3
import datetime

from flask_cors import CORS

from flask import Flask, request, jsonify, render_template
from flask_jwt import JWT, jwt_required, current_identity


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def create_user_table():
    conn = sqlite3.connect('flask_db.db')
    print("Opened database successfully")

    with sqlite3.connect('flask_db.db') as connection:
        conn.execute("CREATE TABLE IF NOT EXISTS user("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "first_name TEXT NOT NULL,"
                     "last_name TEXT NOT NULL,"
                     "username TEXT NOT NULL,"
                     "email_address TEXT NOT NULL,"
                     "address TEXT NOT NULL,"
                     "password TEXT NOT NULL)")

    print("user table created successfully")


def create_product_table():
    conn = sqlite3.connect('flask_db.db')
    print("Opened database successfully")

    with sqlite3.connect('flask_db.db') as connection:
        conn.execute("CREATE TABLE IF NOT EXISTS product("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "category TEXT NOT NULL,"
                     "review TEXT NOT NULL)")

    print("user table created successfully")


def fetch_users():
    with sqlite3.connect('flask_db.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[6]))
    return new_data


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


create_user_table()
create_product_table()
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        address = request.form['address']
        password = request.form['password']
        email_address = request.form['email_address']

        with sqlite3.connect("flask_db.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO user( first_name, last_name, username, email_address, address, password )"
                           f"VALUES( '{first_name}', '{last_name}', '{username}', '{email_address}', '{address}', '{password}' )")
            conn.commit()

            response["message"] = "success"
            response["status_code"] = 201

        return response


@app.route('/add-product/', methods=["POST"])
@jwt_required()
def add_product():
    response = {}

    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        review = request.form['review']

        with sqlite3.connect('flask_db.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO product( name, description, price, category, review )"
                           f"VALUES( '{name}', '{description}', '{price}', '{category}', '{review}' )")
            conn.commit()

            response["status_code"] = 201
            response['description'] = "Product successfully added"

        return response


@app.route('/show-products/', methods=["GET"])
def get_blogs():
    response = {}

    with sqlite3.connect("flask_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    # render_template('index.html')

    return response


@app.route('/view-product/<int:post_id>/', methods=["GET"])
def get_post(post_id):
    response = {}

    with sqlite3.connect("flask_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM product WHERE id={str(post_id)}")

        response["status_code"] = 200
        response["description"] = "Product retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/edit-post/<int:post_id>/', methods=["PUT"])
@jwt_required()
def edit_post(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('flask_db.db') as connection:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")

                with sqlite3.connect('flask_db.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product SET title =? WHERE id=?", (put_data["title"], post_id))
                    connection.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            if incoming_data.get("content") is not None:
                put_data['content'] = incoming_data.get('content')

                with sqlite3.connect('flask_db.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product SET content =? WHERE id=?", (put_data["content"], post_id))
                    connection.commit()

                    response["content"] = "Content updated successfully"
                    response["status_code"] = 200
    return response


@app.route("/delete-product/<int:post_id>", methods=["GET"])
@jwt_required()
def delete_product(post_id):
    response = {}
    with sqlite3.connect("flask_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM product WHERE id={str(post_id)}")
        conn.commit()

        response['status_code'] = 200
        response['message'] = "Product deleted successfully."

    return response