import os
import json
from datetime import datetime

import crud
from model import db, connect_to_db
import server

os.system("dropdb vehicle-services")
os.system("createdb vehicle-services")

connect_to_db(server.app)

with server.app.app_context():
    db.create_all()

    with open('data/users.json') as u:
        user_data = json.loads(u.read())

    users_to_database = []
    for user in user_data:
        username, email, password = (
            user["username"],
            user["email"],
            user["password"]
        )
        db_user = crud.create_user(username, email, password)
        
        users_to_database.append(db_user)

    db.session.add_all(users_to_database)
    db.session.commit()


    with open('data/vehicles.json') as v:
        vehicle_data = json.loads(v.read())

    vehicles_to_database = []
    for vehicle in vehicle_data:
        user_id, vin, make, model, year, use_val, use_unit, vehicle_notes, vehicle_image_link = (
            vehicle["user_id"],
            vehicle["vin"],
            vehicle["make"],
            vehicle["model"],
            vehicle["year"],
            vehicle["use_val"],
            vehicle["use_unit"],
            vehicle["vehicle_notes"],
            vehicle["vehicle_image_link"]
        )
        db_vehicle = crud.create_vehicle(user_id, vin, make, model, year, use_val, use_unit, vehicle_notes, vehicle_image_link)
        
        vehicles_to_database.append(db_vehicle)

    db.session.add_all(vehicles_to_database)
    db.session.commit()

    with open('data/services.json') as s:
        service_data = json.loads(s.read())

    services_to_database = []
    for service in service_data:
        vehicle_id, service_name, service_period, period_count, period_units, service_notes = (
            service["vehicle_id"],
            service["service_name"],
            service["service_period"],
            service["period_count"],
            service["period_units"],
            service["service_notes"]
        )

        db_service = crud.create_service(vehicle_id, service_name, service_period, period_count, period_units, service_notes)

        services_to_database.append(db_service)

    db.session.add_all(services_to_database)
    db.session.commit()
    
    with open('data/occurences.json') as o:
        occurence_data = json.loads(o.read())

    occurences_to_database = []
    for occurence in occurence_data:
        service_id, use_at_service, use_unit_at_service, date_of_service, occurence_notes = (
            occurence["service_id"],
            occurence["use_at_service"],
            occurence["use_unit_at_service"],
            occurence["date_of_service"],
            occurence["occurence_notes"]
        )

        db_occurence = crud.create_occurence(service_id, use_at_service, use_unit_at_service, date_of_service, occurence_notes)

        occurences_to_database.append(db_occurence)

    db.session.add_all(occurences_to_database)
    db.session.commit()
