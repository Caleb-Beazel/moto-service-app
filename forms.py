from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators, IntegerField, SubmitField, SelectField, TextAreaField


class LoginForm(FlaskForm):
    username = StringField('Username: ', [validators.InputRequired()])
    password = PasswordField('Password: ', [validators.InputRequired()])
    submit = SubmitField("Login")

class CreateAccount(FlaskForm):
    username = StringField("Username: ", [validators.InputRequired()])
    email = StringField("Email: ", [validators.InputRequired()])
    password = PasswordField("Password: ", [validators.InputRequired()])
    submit = SubmitField("Create Account")

class AddVehicle(FlaskForm):
    vin = StringField('Vin: ', [validators.InputRequired()])
    make = StringField('Make: ', [validators.InputRequired()])
    model = StringField('Model: ', [validators.InputRequired()])
    year = SelectField('Year: ',[validators.InputRequired()], choices=list(range(2030, 1900, -1)))
    use_val = IntegerField('Use: ', [validators.InputRequired()])
    use_unit = SelectField('Use Units', [validators.InputRequired()], choices=['miles', 'kilometers', 'hours'])
    vehicle_notes = TextAreaField('Notes: ')
    vehicle_image_link = StringField('Image Link: ')
    submit = SubmitField("Add Vehicle")

class EditVehicle(FlaskForm):
    vin = StringField('Vin: ', [validators.InputRequired()])
    make = StringField('Make: ', [validators.InputRequired()])
    model = StringField('Model: ', [validators.InputRequired()])
    year = SelectField('Year: ',[validators.InputRequired()], choices=list(range(2030, 1900, -1)))
    # use_val = IntegerField('Use: ', [validators.InputRequired()])
    use_unit = SelectField('Use Units', [validators.InputRequired()], choices=['miles', 'kilometers', 'hours'])
    vehicle_notes = TextAreaField('Notes: ')
    vehicle_image_link = StringField('Image Link: ')
    submit = SubmitField("Submit Edits")


class AddService(FlaskForm):
    service_name = StringField('Name of Service: ', [validators.InputRequired()])
    service_period = IntegerField('Service Period: ', [validators.InputRequired()])
    period_count = IntegerField('Since Last Service: ', [validators.InputRequired()])
    service_notes = TextAreaField('Notes: ')
    submit = SubmitField("Add Service")

class EditService(FlaskForm):
    service_name = StringField('Name of Service: ', [validators.InputRequired()])
    service_period = IntegerField('Service Period: ', [validators.InputRequired()])
    period_count = IntegerField('Since Last Service: ', [validators.InputRequired()])
    service_notes = TextAreaField('Notes: ')
    submit = SubmitField("Update Service")
