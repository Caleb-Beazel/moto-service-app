from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db, db, User, Vehicle, Service, Occurence
from jinja2 import StrictUndefined
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_manager,login_user, logout_user, current_user
from forms import LoginForm
import crud


app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def homepage():
    login_form = LoginForm()
    return render_template("homepage.html", login_form=login_form)

@app.route("/login", methods=["POST"])
def process_login():
    login_form = LoginForm()
    username = login_form.username.data
    password = login_form.password.data

    user = User.query.filter_by(username=username).first()

    if not user or user.password != password:
        flash("Either the username you provided does not exist or the password was entered incorrectly.")
        return redirect(url_for("homepage"))
    else:
        login_user(user)
        flash(f"Welcome back, {user.username}!")
        return redirect(url_for("homepage"))
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("homepage"))

if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True)