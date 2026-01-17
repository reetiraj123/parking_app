from flask import Flask, render_template, redirect, url_for, request
from models.models import db, init_database, User, Admin
from token_utils import generate_token
from controller.user_controller import user_bp
from controller.admin_controller import admin_bp  


app = Flask(__name__)


# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
init_database(app)

# Register Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)  


# Landing Page
@app.route("/")
def landing():
    return render_template("landing.html")

# Signup Page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_name = request.form["username"]
        full_name = request.form["full_name"]
        password = request.form["password"]

        if User.query.filter_by(user_name=user_name).first():
            return redirect(url_for("login"))

        while True:
            token = generate_token()
            if not User.query.filter_by(token=token).first():
                break
        
        new_user = User(
            user_name=user_name,
            full_name=full_name,
            password=password,
            token=token,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(user_name=user_name).first()
        if user and user.password == password:
            return redirect(url_for("user.dashboard", token=user.token))

        admin = Admin.query.filter_by(username=user_name).first()
        if admin and admin.password == password:
            return redirect(url_for("admin.dashboard"))  

        return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

