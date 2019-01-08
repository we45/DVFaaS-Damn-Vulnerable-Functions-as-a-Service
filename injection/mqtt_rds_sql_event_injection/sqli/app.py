from chalice import Chalice
from os import environ
from random import uniform
from json import loads
import pymysql.cursors

app = Chalice(app_name='dvfaas-event-injection-sqli')

db = pymysql.connect(
    host = environ['DB_HOST'],
    user = environ['DB_USER'],
    password = environ['DB_PASS'],
    db = environ['DB_DB']
)


@app.route('/test_insert')
def index():
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO sensor_temperature (sensor_name, temperature) VALUES ('%s', '%s')" % ('sensor_name_2', '60.0'))

        db.commit()
        return {"success": "inserted sensor value"}
    except Exception as e:
        print(e)
        return {"error": e.__str__()}

@app.on_sns_message(topic="sensor_channel")
def sensor_react(event):
    try:
        event_dict = loads(event.message)
        sensor_name = event.subject
        if 'reading' in event_dict:
            with db.cursor() as cur:
                cur.execute("INSERT INTO sensor_temperature (sensor_name, temperature) VALUES ('%s',%s)" % (sensor_name, event_dict['reading']))

            db.commit()
            print("Successfully inserted values: {} and {} into the sensor temperature table".format(sensor_name, event_dict['reading']))
    except Exception as e:
        print(e)