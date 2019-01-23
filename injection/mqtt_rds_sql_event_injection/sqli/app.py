from chalice import Chalice, BadRequestError
from os import environ
from random import uniform
from json import loads, dumps
import pymysql.cursors
import boto3

app = Chalice(app_name='dvfaas-event-injection-sqli')
topic_arn = environ['SNS_TOPIC']

db = pymysql.connect(
    host = environ['DB_HOST'],
    user = environ['DB_USER'],
    password = environ['DB_PASS'],
    db = environ['DB_DB']
)

client = boto3.client('sns')


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

@app.route('/publish/{name}', methods = ['POST'], content_types=['application/json'])
def pub_message(name):
    try:
        jbody = app.current_request.json_body
        if 'reading' in jbody:
            str_reading = str(jbody['reading'])
            response = client.publish(
                TopicArn='arn:aws:sns:us-east-1:358174707935:sensor_channel',
                Subject=name,
                Message=dumps({"reading": "{}".format(str_reading)})
            )
            return {"success": "published reading"}
        else:
            return BadRequestError("Invalid data. Must contain reading")
    except Exception as e:
        return BadRequestError(str(e))



@app.on_sns_message(topic=topic_arn)
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