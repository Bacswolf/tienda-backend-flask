# imoports
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

# application init
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SECRET_KEY"] = "secret-key"
# database init
db = SQLAlchemy(app)

# login manager init
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# database tables
class User(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"<User{self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    desciption = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product{self.title}>"


# routes
@app.route("/")
def home():
    products = Product.query.all()  # get all products from database
    return render_template("home.html", products=products)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        # check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))

        return "<h1>Invalid username or password</h1>"
    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# product routes
# add product
@app.route("/product", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        price = request.form["price"]
        product = Product(title=title, desciption=description, price=price)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("product.html")


# update product
@app.route("/product/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_product(id):
    if request.method == "GET":
        product = Product.query.get(id)
        return render_template("update.html", dataproduct=product)
    elif request.method == "POST":
        product = Product.query.get(id)
        product.title = request.form["title"]
        product.desciption = request.form["description"]
        product.price = request.form["price"]
        db.session.commit()
        return redirect(url_for("home"))


# delete product
@app.route("/product/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for("list"))


@app.route("/list")
def list():
    products = Product.query.all()  # get all products from database
    return render_template("list.html", products=products)


# run application
if __name__ == "__main__":
    app.run(debug=True)
