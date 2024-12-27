# Import the dependencies.
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite://Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
# reflect the tables
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# 1. import Flask

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return ("Welcome to my Home page!<br/><br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/&lt;start&gt;<br/>"
            f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# 4. Define what to do when a user hits the /about route
@app.route("/about")
def about():
    print("Server received request for 'About' page...")
    return "Welcome to my 'About' page!"


if __name__ == "__main__":
    app.run(debug=True)
    


#################################################
# Flask Routes
#################################################

# Flask Routes


# Precipitation route to return the last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()
    precip_data = {date: prcp for date, prcp in results}
    return jsonify(precip_data)

# Stations route to return a list of stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    station_list = [station[0] for station in results]
    return jsonify(station_list)

# Temperature Observations (tobs) route to return the temperature data for the most active station for the last year
@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    most_active_station = session.query(measurement.station).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()[0]
    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station).filter(measurement.date >= one_year_ago).all()
    tobs_data = [{date: tobs} for date, tobs in results]
    return jsonify(tobs_data)

# 5. Start and start/end route to return TMIN, TAVG, TMAX
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start, end=None):
    if end is None:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    else:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    temp_stats = list(results[0])
    return jsonify(temp_stats)
if __name__ == "__main__":
    app.run(debug=True)