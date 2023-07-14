from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db
from jinja2 import StrictUndefined
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required

import crud

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
@login_required
def homepage():
    return render_template("homepage.html")

@app.route("/login", methods=["POST"])
def process_login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = crud.get_user_by_username(username)

    if not user or user.password != password:
        flash("Either the username you provided does not exist or the password was entered incorrectly.")

    else:
        session["username"] = user.username
        flash(f"Welcome back, {user.username}!")

if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True)