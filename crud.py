from model import db, User, Vehicle, Service, Occurence, connect_to_db

def create_user(username, email, password):
    user = User(
        username=username,
        email=email,
        password=password
        )
    
    return user

def get_users():

    return User.query.all()

def get_user_by_id(user_id):
    
    return User.query.get(user_id)

def get_user_by_username(username):
    
    return User.query.filter(User.username == username).first() 

def create_vehicle(user_id, vin, make, model, year, use_val, use_unit, vehicle_notes = None, vehicle_image_link = None):
    vehicle = Vehicle(
        user_id=user_id,
        vin=vin,
        make=make,
        model=model,
        year=year,
        use_val=use_val,
        use_unit=use_unit,
        vehicle_notes=vehicle_notes,
        vehicle_image_link=vehicle_image_link
        )
    
    return vehicle

def create_service(vehicle_id, service_name, service_period, period_count, period_units,service_notes):
    service = Service(
        vehicle_id=vehicle_id,
        service_name=service_name,
        service_period=service_period,
        period_count=period_count,
        period_units=period_units,
        service_notes=service_notes
        )
    
    return service

def create_occurence(service_id, use_at_service, use_unit_at_service, date_of_service, occurence_notes):
    occurence = Occurence(
        service_id=service_id,
        use_at_service=use_at_service,
        use_unit_at_service=use_unit_at_service,
        date_of_service=date_of_service,
        occurence_notes=occurence_notes
    
        )
    return occurence

if __name__ == '__main__':
    from server import app
    connect_to_db(app)