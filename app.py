from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#Reflect tables into SQLAlchemy
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model Feb 14-28, 2020)
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app=Flask(__name__)

#Define home page - create a list of each route and what it shows
# Dictionary of all the routes
usage_dict = [
    {"route": "/api/v1.0/precipitation", "info": "Precipitation data by date"},
    {"route": "/api/v1.0/stations", "info": "List of weather stations"},
    {"route": "/api/v1.0/tobs", "info": "Temperature observation by date in last year"},
    {"route": "/api/v1.0/<start>", "info": "Find weather information for a given date"},
    {"route": "/api/v1.0/<start>/<end>", "info": "Find weather information for a given date ranges"}
]

@app.route("/")
def home():
    return jsonify(usage_dict)

#Define precipitation page
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query date & prcp data
    prcp_data = session.query(Measurement.date, Measurement.prcp)
    
    session.close()
    
    #Write prcp info to dict
    prcp_dict={}
    
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)

#Define station page
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query station names
    station_list = session.query(Station.name)
    
    session.close()
    
    #Write station info to dict
    station_names=[]
    
    for entry in station_list:
        station_names.append(entry)
    
    return jsonify(station_names)

# #Define page to show last year of data for most active stations
# @app.route("/api/v1.0/tobs")
# def tobs():
    
    
#     return jsonify(justice_league_members)

# #Define page to return info for a given date
# @app.route("/api/v1.0/<start>")
# def jsonified():
#     return jsonify(justice_league_members)

# #Define page to return date range
# @app.route("/api/v1.0/<start>/<end>")
# def jsonified():
#     return jsonify(justice_league_members)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)