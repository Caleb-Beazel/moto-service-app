import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_name = db.Column(db.String(255), unique = True)
    email = db.Column(db.String(255), unique = True)
    password = db.Column(db.String(255))

    def __repr__(self):
        return f"{self.user_name} | ID = {self.user_id} | Email = {self.email}"

class Vehicle(db.Model):

    __tablename__ = "vehicles"

    vehicle_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable = False)
    vin = db.Column(db.String, unique = True, nullable = False)
    make = db.Column(db.String(255), nullable = False)
    model = db.Column(db.String(255), nullable = False)
    year = db.Column(db.Integer, nullable = False)
    use_val = db.Column(db.Integer, nullable = False)
    use_unit = db.Column(db.String, default = "hours", nullable = False)
    vehicle_notes = db.Column(db.String)
    vehicle_image_link = db.Column(db.String)

    def __repr__(self):
        return f"{self.year} {self.make} {self.model} ::: {self.use_val} {self.use_unit} ::: User ID: {self.user_id}"
    
class Service(db.Model):

    __tablename__ = "services"

    service_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.vehicle_id"), nullable = False)
    service_name = db.Column(db.String, nullable = False)
    service_period = db.Column(db.Integer, nullable = False)
    period_count = db.Column(db.Integer, nullable = False, default = 0)
    period_units = db.Column(db.String, nullable = False)
    

    def __repr__(self):
        return f"{self.service_name} -- Next Service: {self.service}"

    def next_service(self):
        return self.service_period - self.period_count
    
class Occurence(db.Model):
    #logs past services so that this info need not be added to the service table
    __tablename_ = "service_occurences"

    occurence_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.service_id"), nullable = False)
    use_val = db.Column(db.Integer, db.ForeignKey("vehicles.use_val"), nullable = False)
    use_unit = db.Column(db.String, db.ForeignKey("vehicles.use_unit"), nullable = False)
    date_of_service = db.Column(db.String, nullable = False)


def connect_to_db(flask_app, db_uri=os.environ["POSTGRES_URI"], echo=False):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")

if __name__ == "__main__":
    from server import app
    connect_to_db(app)