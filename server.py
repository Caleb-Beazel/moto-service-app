from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db, db, User, Vehicle, Service, Occurence
from jinja2 import StrictUndefined
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_manager,login_user, logout_user, current_user
from forms import LoginForm, CreateAccount
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
    new_account_form = CreateAccount()
    
    return render_template("homepage.html", login_form=login_form, new_account_form=new_account_form)

@app.route("/new-account", methods=["POST"])
def new_account():
    new_account_form = CreateAccount()
    username = new_account_form.username.data
    email = new_account_form.email.data
    password = new_account_form.password.data

    existing_username = User.query.filter_by(username=username).first()
    existing_email = User.query.filter_by(email=email).first()

    if existing_username:
        flash(f"An account with the username {username} already exists in our system. Please try another.")
    elif existing_email:
        flash(f"We already have an account on file for {email}.")
    else:
        user = crud.create_user(username, email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in to begin.")
    return redirect("/")

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
        return redirect(url_for("user_home"))
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/user-home")
@login_required
def user_home():

    user_services = Service.query.join(Vehicle).filter(Vehicle.user_id == current_user.user_id).all()
    
    return render_template("user_home.html", user_services=user_services)

if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True)