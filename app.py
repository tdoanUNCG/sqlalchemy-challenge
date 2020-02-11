# import dependencies
from flask import Flask, jsonify, request
import datetime as dt
import numpy as np

# sqlalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, and_

# path to sqlite db
database_path = 'Resources/hawaii.sqlite'

# create an engine to communicate with db
engine = create_engine(f'sqlite:///{database_path}')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine)

# create app
app = Flask(__name__)

# define routes
@app.route('/')
def index():
    return "<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br>\
    <a href='/api/v1.0/stations'>/api/v1.0/stations</a><br>\
    <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br>\
    * start and end date format: yyyy-mm-dd<br>\
    /api/v1.0/start<br>\
    /api/v1.0/start/end"

@app.route('/api/v1.0/precipitation')
def prcp():
    #create session engine link
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    # create dictionary for all row of data and append to all_data
    all_data = []
    for date, prcp in results:
        all_data_dict = {}
        all_data_dict[date] = prcp
        all_data.append(all_data_dict)
    return jsonify(all_data)

@app.route('/api/v1.0/stations')
def stations():
    # create session engine link
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    # convert list of tuples to normal list
    all_data = list(np.ravel(results))

    return jsonify(all_data)

@app.route('/api/v1.0/tobs')
def tobs():

    #create session engine link
    session = Session(engine)
    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    # Extract date string only
    sliced_date = last_date[2:12]

    # extract year, month, day, from string and convert to int
    year = int(sliced_date[0:4])
    month = int(sliced_date[5:7])
    day = int(sliced_date[8:10])

    # query date that was a year ago from last date
    one_year_ago = dt.date(year,month,day) - dt.timedelta(days=365)

    # query tobs from latest date back to a year one_year_ago
    last_one_year = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date>=one_year_ago).order_by(Measurement.date).all()

    session.close()
    all_data = []
    for date, tobs in last_one_year:
        all_data_dict = {}
        all_data_dict[date] = tobs
        all_data.append(all_data_dict)
    return jsonify(all_data)

@app.route('/api/v1.0/<start>')
def start_date(start):
    # create session engine link
    session = Session(engine)
    sel = [func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date>=start).first()
    # close session link
    session.close()
    min = results[0]
    avg = results[1]
    max = results[2]
    new_dict = {'min temp': min, 'avg temp': avg, 'max temp':max}
    return jsonify(new_dict)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    # create session engine link
    session = Session(engine)
    sel = [func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date>=start,Measurement.date<=end).first()
    # close session link
    session.close()
    min = results[0]
    avg = results[1]
    max = results[2]
    new_dict = {'min temp': min, 'avg temp': avg, 'max temp':max}
    return jsonify(new_dict)
# for fun
# def start_end():
#     # create request args
#     start_date = request.args.get('start_date')
#     end_date = request.args.get('end_date')
#     #create session engine link
#     session = Session(engine)
#     if start_date and end_date:
#         results = session.query(Measurement.date,Measurement.tobs).\
#         filter(and_(Measurement.date>=start_date,Measurement.date<=end_date)).\
#         order_by(Measurement.date).all()
#         session.close()
#         all_data = []
#         for date, tobs in results:
#             all_data_dict = {}
#             all_data_dict[date] = tobs
#             all_data.append(all_data_dict)
#         return jsonify(all_data)
#     elif start_date:
#         results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>=start_date).all()
#         session.close()
#         all_data = []
#         for date, tobs in results:
#             all_data_dict = {}
#             all_data_dict[date] = tobs
#             all_data.append(all_data_dict)
#         return jsonify(all_data)

# define main behavior
if __name__ == '__main__':
    app.run(debug=True)
