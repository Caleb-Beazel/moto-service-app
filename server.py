from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db, db, User, Vehicle, Service, Occurence
from jinja2 import StrictUndefined
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_manager,login_user, logout_user, current_user
from forms import LoginForm, CreateAccount, AddVehicle, EditVehicle
import crud


app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# User Login endpoints

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

# Main user interface page

@app.route("/user-home")
@login_required
def user_home():

    user_services = Service.query.join(Vehicle).filter(Vehicle.user_id == current_user.user_id).all()

    sorted_user_services = sorted(user_services, key = lambda x: (x.period_count / x.service_period), reverse=True)

    return render_template("user_home.html", user_services=sorted_user_services)

# Vehicle Endpoints

# Create Vehicle Page
@app.route("/user-home/vehicles/add")
@login_required
def new_vehicle_form():
    new_vehicle = AddVehicle()
    return render_template("vehicle_new.html", new_vehicle=new_vehicle)

# Create a Vehicle
@app.route("/user-home/vehicles/add/new-vehicle", methods=["POST"])
@login_required
def create_new_vehicle():
    new_vehicle = AddVehicle()

    user_id = current_user.user_id
    vin = new_vehicle.vin.data
    make = new_vehicle.make.data
    model = new_vehicle.model.data
    year = new_vehicle.year.data
    use_val = new_vehicle.use_val.data
    use_unit = new_vehicle.use_unit.data
    vehicle_notes = new_vehicle.vehicle_notes.data
    vehicle_image_link = new_vehicle.vehicle_image_link.data


    vehicle = crud.create_vehicle(user_id, vin, make, model, year, use_val, use_unit, vehicle_notes, vehicle_image_link)

    db.session.add(vehicle)
    db.session.commit()
    flash(f"A {year} {make} {model} has been added to your account.")

    return redirect("/user-home")
    


@app.route("/user-home/vehicles/<vehicle_id>/edit", methods=["GET", "UPDATE"])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    edit_vehicle = EditVehicle(obj=vehicle)

    return render_template("vehicle_edit.html", edit_vehicle=edit_vehicle, vehicle=vehicle)


@app.route("/user-home/vehicles/<vehicle_id>/edit/submit", methods=["GET", "POST"])
@login_required
def submit_edit_vehicle(vehicle_id):
    vehicle_to_update = Vehicle.query.get(vehicle_id)
    vehicle_updates = EditVehicle()

    vehicle_to_update.vin = vehicle_updates.vin.data
    vehicle_to_update.make = vehicle_updates.make.data
    vehicle_to_update.model = vehicle_updates.model.data
    vehicle_to_update.year = vehicle_updates.year.data
    vehicle_to_update.use_val = vehicle_updates.use_val.data
    vehicle_to_update.use_unit = vehicle_updates.use_unit.data
    vehicle_to_update.vehicle_notes = vehicle_updates.vehicle_notes.data
    vehicle_to_update.vehicle_image_link = vehicle_updates.vehicle_image_link.data

    db.session.commit()

    flash("Your vehicle has been updated.")

    return redirect(f"/user-home/vehicles/{vehicle_id}")


@app.route("/user-home/vehicles/<vehicle_id>")
@login_required
def vehicle_details(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    return render_template("vehicle_details.html", vehicle_id=vehicle_id, vehicle=vehicle)


@app.route("/user-home/vehicles/<vehicle_id>/delete")
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    services = Service.query.filter(Service.vehicle_id == vehicle_id).all()
    for service in services:
        occurences = Occurence.query.filter(Occurence.service_id == service.service_id).all()
        
        for occurence in occurences:
            db.session.delete(occurence)
        
        db.session.delete(service)
    db.session.delete(vehicle)

    db.session.commit()

    flash("Your vehicle and it's associated services have been deleted.")

    return redirect("/user-home")




# Service Endpoints

@app.route("/user-home/services/<service_id>")
@login_required
def service_details(service_id):
    service = Service.query.get(service_id)
    
    return render_template("service_details.html", service_id=service_id, service=service)


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True)