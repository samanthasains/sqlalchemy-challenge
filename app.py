from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
@app.route("/")
def home():
    return  (
        f"Welcome & please find instructions for use to find our information about weather in Hawaii!<br/>"
        f"Available Routes are listed below:<br/>"
        f"Precipitation data by date: /api/v1.0/precipitation<br/>"
        f"List of Weather Stations: /api/v1.0/stations<br/>"
        f"Temperature for the last year recorded: /api/v1.0/tobs<br/>"
        f"Temperature statistics from the start date between 2010-01-01 and 2017-08-23 using the following format (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature statistics from start to end date between 2010-01-01 and 2017-08-23 using the following format (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

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

# #Define page to show last year of data for most active station
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #first and last dates
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date 1 year ago from the last data point in the database
    last_date_formatted = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    last_year_date = dt.date(last_date_formatted.year -1, last_date_formatted.month, last_date_formatted.day)

    # List the stations and the counts in descending order.
    count_by_station =  session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()
    
    most_active_id=(list(count_by_station[0]))[0]

    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    data_temp = (Measurement.date, Measurement.tobs)

    temp_data = session.query(*data_temp).\
        filter(Measurement.station == most_active_id).\
        filter(Measurement.date >= last_year_date).all()

    session.close()

    #Write temp info to dict
    temps_list = []
    
    for date, temp in temp_data:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['Temperature'] = temp
        temps_list.append(temp_dict)
    
    return jsonify(temps_list)

# #Define page to return info for a given date
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query info
    results = session.query(Measurement.date, func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                            group_by(Measurement.date).all()
    
    session.close()
    
    #Write to dictionary
    temp_summary_dict = []
    
    for date, max, min, avg in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["Max Temp"] = max
        new_dict["Min Temp"] = min
        new_dict["Temp Average"] = avg
        temp_summary_dict.append(new_dict)


    return jsonify(temp_summary_dict)

# #Define page to return date range
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query info
    results = session.query(Measurement.date, func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).\
                        group_by(Measurement.date).all()    
    
    session.close()
    
    #Write to dictionary
    temp_summary_dict = []
    
    for date, max, min, avg in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["Max Temp"] = max
        new_dict["Min Temp"] = min
        new_dict["Temp Average"] = avg
        temp_summary_dict.append(new_dict)


    return jsonify(temp_summary_dict)
    

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)