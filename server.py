from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db, db, User, Vehicle, Service, Occurence
from jinja2 import StrictUndefined
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_manager,login_user, logout_user, current_user
from forms import LoginForm, CreateAccount, AddVehicle, EditVehicle, AddService, EditService, AddOccurence
import crud
from datetime import datetime

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# ------ User Endpoints -------

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

    sorted_user_services = sorted(user_services, key = lambda x: (x.period_count - x.service_period), reverse=True)

    return render_template("user_home.html", user_services=sorted_user_services)

# ---- Vehicle Endpoints -----

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
    

# Edit Vehicle Page
@app.route("/user-home/vehicles/<vehicle_id>/edit")
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    edit_vehicle = EditVehicle(obj=vehicle)

    return render_template("vehicle_edit.html", edit_vehicle=edit_vehicle, vehicle=vehicle)

# Submit Vehicle Edit
@app.route("/user-home/vehicles/<vehicle_id>/edit/submit", methods=["GET", "POST"])
@login_required
def submit_edit_vehicle(vehicle_id):
    vehicle_to_update = Vehicle.query.get(vehicle_id)
    vehicle_updates = EditVehicle()
    vehicle_services = Service.query.filter_by(vehicle_id=vehicle_id).all()

    use_val_diff = vehicle_updates.use_val.data - vehicle_to_update.use_val

    vehicle_to_update.vin = vehicle_updates.vin.data
    vehicle_to_update.make = vehicle_updates.make.data
    vehicle_to_update.model = vehicle_updates.model.data
    vehicle_to_update.year = vehicle_updates.year.data
    vehicle_to_update.use_val = vehicle_updates.use_val.data
    vehicle_to_update.use_unit = vehicle_updates.use_unit.data
    vehicle_to_update.vehicle_notes = vehicle_updates.vehicle_notes.data
    vehicle_to_update.vehicle_image_link = vehicle_updates.vehicle_image_link.data

    for service in vehicle_services:
        service.period_count += use_val_diff

    db.session.commit()

    flash("Your vehicle has been updated.")

    return redirect(f"/user-home/vehicles/{vehicle_id}")

# Vehicle Details Page / Vehicle Services
@app.route("/user-home/vehicles/<vehicle_id>")
@login_required
def vehicle_details(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    all_services = Service.query.filter_by(vehicle_id=vehicle_id).all()
    
    services = sorted(all_services, key = lambda x: (x.period_count - x.service_period), reverse=True)

    return render_template("vehicle_details.html", vehicle_id=vehicle_id, vehicle=vehicle, services=services)

# Delete A Vehicle
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


# ----- Service Endpoints ------

# Service Details / Display Occurences
@app.route("/user-home/services/<service_id>")
@login_required
def service_details(service_id):
    service = Service.query.get(service_id)
    occurences = Occurence.query.filter_by(service_id=service_id).all()
    
    return render_template("service_details.html", service_id=service_id, service=service, occurences=occurences)

# Add a Service to Vehicle
@app.route("/user-home/vehicles/<vehicle_id>/add-service")
@login_required
def new_service_form(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    new_service = AddService()
    return render_template("service_new.html", new_service=new_service, vehicle=vehicle)

# Submit Add New Service
@app.route("/user-home/vehicles/<vehicle_id>/add-service/submit", methods=["GET", "POST"])
@login_required
def create_new_service(vehicle_id):

    new_service = AddService()
    vehicle = Vehicle.query.get(vehicle_id)

    vehicle_id = vehicle_id
    service_name = new_service.service_name.data
    service_period = new_service.service_period.data
    period_count = new_service.period_count.data
    period_units = vehicle.use_unit
    service_notes = new_service.service_notes.data

    service = crud.create_service(vehicle_id, service_name, service_period, period_count, period_units, service_notes)

    db.session.add(service)
    db.session.commit()

    flash(f"Service: - {service_name} - has been added to your {vehicle.year} {vehicle.make} {vehicle.model}.")

    return redirect(f"/user-home/vehicles/{vehicle_id}")


# Edit Existing Service
@app.route("/user-home/vehicles/services/<service_id>/edit")
@login_required
def edit_service(service_id):
    service = Service.query.get(service_id)
    edit_service = EditService(obj=service)

    return render_template("service_edit.html", edit_service=edit_service, service=service)

# Submit Edited Service
@app.route("/user-home/vehicles/services/<service_id>/edit/submit", methods=["GET", "POST"])
@login_required
def submit_edit_service(service_id):

    service_to_update = Service.query.get(service_id)
    service_updates = EditService()

    service_to_update.service_name = service_updates.service_name.data
    service_to_update.service_period = service_updates.service_period.data
    service_to_update.period_count = service_updates.period_count.data
    service_to_update.service_notes = service_updates.service_notes.data

    db.session.commit()

    flash(f"{service_to_update.service_name} has been updated.")
    return redirect(f"/user-home/services/{service_id}")

# Delete Service
@app.route("/user-home/services/<service_id>/delete")
@login_required
def delete_service(service_id):
    service = Service.query.get(service_id)
    occurences = Occurence.query.filter(Occurence.service_id == service.service_id).all()
        
    for occurence in occurences:
        db.session.delete(occurence)
    
    db.session.delete(service)

    db.session.commit()

    flash(f"{service.service_name} and it's associated occurences have been deleted.")

    return redirect(f"/user-home/vehicles/{service.vehicle_id}")


# ------ Occurence Endpoints -------

# Add Occurence
@app.route("/user-home/services/<service_id>/complete")
@login_required
def new_occurence_form(service_id):
    service = Service.query.get(service_id)
    new_occurence = AddOccurence()
    return render_template("occurence_new.html",service=service, new_occurence=new_occurence)


# Submit Occurence
@app.route("/user-home/services/<service_id>/complete/submit", methods=["GET", "POST"])
@login_required
def create_new_occurence(service_id):
    service = Service.query.get(service_id)
    vehicle = Vehicle.query.get(service.vehicle_id)
    new_occurence = AddOccurence()
    
    use_at_service = vehicle.use_val
    use_unit_at_service = vehicle.use_unit 
    date_of_service = new_occurence.date_of_service.data
    occurence_notes = new_occurence.occurence_notes.data

    service.period_count = 0

    occurence = crud.create_occurence(service_id, use_at_service, use_unit_at_service, date_of_service, occurence_notes)

    db.session.add(occurence)
    db.session.commit()

    flash(f"{service.service_name} serviced for: {vehicle.year} {vehicle.make} {vehicle.model}.")
    
    return redirect(f"/user-home/services/{service_id}")

# Delete Occurence
@app.route("/user-home/services/occurences/<occurence_id>/delete")
@login_required
def delete_occurence(occurence_id):
    occurence = Occurence.query.get(occurence_id)

    db.session.delete(occurence)
    db.session.commit()

    flash(f"Occurence was deleted.")
    
    return redirect(f"/user-home/services/{occurence.service_id}")

if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True)