import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Station = Base.classes.station
Measurement = Base.classes.measurement


app = Flask(__name__) 

@app.route("/")
def home():
    all_routes = ['/api/v1.0/precipitation','/api/v1.0/stations', '/api/v1.0/tobs','/api/v1.0/<start>','/api/v1.0/<start>/<end>']
    return jsonify(all_routes)

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    start_date = dt.datetime.strptime(last_date, '%Y-%m-%d').date() - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    col_selected = [Measurement.date, Measurement.prcp]
    prcp_1year = session.query(*col_selected).filter(Measurement.date > start_date).all()
    prcp_dict = {}
    for i in range(len(prcp_1year)):
        prcp_dict[prcp_1year[i][0]] = prcp_1year[i][1]

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_rows = session.query(Measurement.station).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    
    return jsonify(station_rows)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    last_date = session.query(func.max(Measurement.date)).scalar()
    start_date = dt.datetime.strptime(last_date, '%Y-%m-%d').date() - dt.timedelta(days=365)
    station_rows = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    most_active_station = station_rows[0][0]
    tobs_selected = [Measurement.date, Measurement.tobs]
    tobs_1year = session.query(*tobs_selected).filter(Measurement.date > start_date).\
        filter(Measurement.station == most_active_station).group_by('date').all()
    return jsonify(tobs_1year)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    return jsonify(result)

@app.route('/api/v1.0/<start>/<end>')
def startend(start, end):
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug = True)

