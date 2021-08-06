import hmac
import sqlite3

from flask_cors import CORS
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_mail import Mail, Message


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def create_user_table():
    print("Opened database successfully")

    with sqlite3.connect('flask_db.db') as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS user("
                           "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                           "first_name TEXT NOT NULL,"
                           "last_name TEXT NOT NULL,"
                           "username TEXT NOT NULL,"
                           "email_address TEXT NOT NULL,"
                           "address TEXT NOT NULL,"
                           "password TEXT NOT NULL)")

    print("user table created successfully")


def create_product_table():
    print("Opened database successfully")

    with sqlite3.connect('flask_db.db') as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS product("
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
        db_users = cursor.fetchall()

        new_data = []

        for data in db_users:
            print(data)
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
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=86400)
CORS(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ndj6851@gmail.com'
app.config['MAIL_PASSWORD'] = 'dejager001!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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
                           f"VALUES( '{first_name}', '{last_name}', '{username}', '{email_address}', '{address}', "
                           f"'{password}' )")
            conn.commit()

            response["message"] = "success"
            response["status_code"] = 201
            if response['status_code'] == 201:
                msg = Message('Email', sender='ndj6851@gmail.com', recipients=[email_address])
                msg.body = "You are successfully Login in"
                mail.send(msg)
            return "Email Sent"


@app.route("/user-login/", methods=["POST"])
def login():
    response = {}

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("flask_db.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
            user_information = cursor.fetchone()

        if user_information:
            response["user_info"] = user_information
            response["message"] = "Success"
            response["status_code"] = 201
            return jsonify(response)

        else:
            response['message'] = "Login Unsuccessful, please try again"
            response['status_code'] = 401
            return jsonify(response)


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
def show_products():
    response = {}

    with sqlite3.connect("flask_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products

    return response


@app.route('/view-product/<int:product_id>/', methods=["GET"])
def view_product(product_id):
    response = {}

    with sqlite3.connect("flask_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM product WHERE id={str(product_id)}")

        response["status_code"] = 200
        response["description"] = "Product retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
@jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        print(request.json)
        incoming_data = dict(request.json)

        put_data = {}

        print(incoming_data.get("name"))
        if incoming_data.get("name") is not None:
            put_data["name"] = incoming_data.get("name")

            with sqlite3.connect('flask_db.db') as connection:
                cursor = connection.cursor()
                cursor.execute(f"UPDATE product SET name = '{str(put_data['name'])}' WHERE id = {str(product_id)}")
                connection.commit()
                response['message'] = "Update was successfully"
                response['status_code'] = 200

        if incoming_data.get("description") is not None:
            put_data['description'] = incoming_data.get('description')
            print(put_data)

            with sqlite3.connect('flask_db.db') as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"UPDATE product SET description = '{str(put_data['description'])}' WHERE id = {str(product_id)}")
                connection.commit()

                response["message"] = "Content updated successfully"
                response["status_code"] = 200

        if incoming_data.get("price") is not None:
            put_data['price'] = incoming_data.get('price')

            with sqlite3.connect('flask_db.db') as connection:
                cursor = connection.cursor()
                cursor.execute(f"UPDATE product SET price = '{str(put_data['price'])}' WHERE id = {str(product_id)}")
                connection.commit()

                response["content"] = "Content updated successfully"
                response["status_code"] = 200

        if incoming_data.get("category") is not None:
            put_data['category'] = incoming_data.get('category')

            with sqlite3.connect('flask_db.db') as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"UPDATE product SET category = '{str(put_data['category'])}' WHERE id = {str(product_id)}")
                connection.commit()

                response["content"] = "Content updated successfully"
                response["status_code"] = 200

        if incoming_data.get("review") is not None:
            put_data['review'] = incoming_data.get('review')

            with sqlite3.connect('flask_db.db') as connection:
                cursor = connection.cursor()
                cursor.execute(f"UPDATE product SET review = '{str(put_data['review'])}'  WHERE id = {str(product_id)}")
                connection.commit()

                response["content"] = "Content updated successfully"
                response["status_code"] = 200
    return response


@app.route("/delete-product/<int:product_id>", methods=["GET"])
@jwt_required()
def delete_product(product_id):
    response = {}
    with sqlite3.connect("flask_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM product WHERE id={str(product_id)}")
        conn.commit()

        response['status_code'] = 200
        response['message'] = "Product deleted successfully."

    return response


if __name__ == '__main__':
    app.run()
