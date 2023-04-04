# Import the dependencies
import sqlalchemy
from flask import Flask, jsonify
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/sulta/OneDrive/Desktop/Boot_Camp_Data_Analytics/Module_10_Advanced_SQL/Module_10_Challenge/Starter_Code/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def main():
    return (
        f"Welcome to the Climate App Home Page.<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    prev_year = dt.date(2017,8,23)- dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).\
                order_by(Measurement.date).all()
    result_dict = dict(results)
    session.close()
    return jsonify(result_dict)


@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    all_names = list(np.ravel(stations))

    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():

    """
    Query the dates and temperature observations of the most-active station for the previous year of data.

    Return a JSON list of temperature observations for the previous year.
    """
    max_temp_obs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').filter(Measurement.station == 'USC00519281').all()

    tobs_dict = dict(max_temp_obs)
    session.close()
    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start>")
def start(start):

    start_time = dt.datetime.strptime(start, "%Y-%m-%d")

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_time).all()
    
    session.close()
    tobsall = []

    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)
        
    return jsonify(tobsall)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    start_time = dt.datetime.strptime(start, "%Y-%m-%d")
    end_time = dt.datetime.strptime(end, "%Y-%m-%d")
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_time).\
        filter(Measurement.date <= end_time).all()

    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


if __name__ == '__main__':
    app.run(debug=True)