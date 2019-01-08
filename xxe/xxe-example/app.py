from chalice import Chalice, BadRequestError, UnauthorizedError
import boto3
from base64 import b64encode
from io import StringIO, BytesIO
from time import sleep
import jwt
from boto3.dynamodb.conditions import Attr
import cgi
from uuid import uuid4
from xml.dom.pulldom import START_ELEMENT, parse, parseString
from os import environ
import hashlib

app = Chalice(app_name='dvfaas-xxe')
dynamo = boto3.resource('dynamodb')
HMAC_PASSWORD_2 = 'super-secret-value'
CV_TBL = environ['CV_TABLE']
CV_BUCKET = environ['TRAINING_BUCKET']
CV_USR_TBL = environ['USER_TABLE']


def get_user_for_event(event_key):
    try:
        print(event_key)
        table = dynamo.Table(CV_TBL)
        resp = table.get_item(Key={'filename': event_key})
        if 'Item' in resp:
            print(resp['Item'])
            return resp['Item']['email']
    except Exception as e:
        app.log.error(e)
        return None


@app.on_s3_event(bucket=CV_BUCKET, events=['s3:ObjectCreated:*'])
def cv_event_handler(event):
    print("Received event for bucket: {}, key: {}".format(event.bucket, event.key))
    file_name = event.key
    s3 = boto3.resource('s3')
    try:
        sleep(2)
        email = get_user_for_event(file_name)
        if email:
            docfile = s3.Object(CV_BUCKET, file_name)
            docbody = docfile.get()['Body'].read()
            doc = parseString(docbody.decode('utf-8'))
            content = ''
            for event, node in doc:
                doc.expandNode(node)
                content = node.toxml()
            try:
                print("content", content)
                cv_table = dynamo.Table(CV_TBL)
                response = cv_table.get_item(Key={'filename': file_name})
                item = response['Item']
                item['file_content'] = b64encode(content.encode()).decode('utf-8')
                cv_table.put_item(Item=item)
                app.log.debug(response)
            except Exception as e:
                print(e.message)

        else:
            raise Exception("Unable to find email")

    except Exception as e:
        print(e)


def is_valid_jwt(token):
    if 'username' in token:
        table = dynamo.Table(CV_USR_TBL)
        resp = table.scan(Select='ALL_ATTRIBUTES', FilterExpression=Attr('username').eq(token.get('username')))
        print(resp)
        if 'Items' in resp:
            return resp['Items']
        else:
            raise Exception("Unable to verify user role")
    else:
        raise Exception("Token doesnt have required value")


@app.route('/signup', methods = ['POST'], content_types=['application/json'], cors = True)
def signup_user():
    try:
        jbody = app.current_request.json_body
        mandatory_attrs = ('email', 'username', 'password', 'first_name', 'last_name')
        if all(k in jbody for k in mandatory_attrs):
            table = dynamo.Table(CV_USR_TBL)
            jbody['password'] = hashlib.md5(jbody['password'].encode()).hexdigest()
            table.put_item(Item = jbody)
            return {"success": jbody}
        else:
            return BadRequestError("Mandatory fields have not been provided")
    except Exception as e:
        return BadRequestError(str(e))

@app.route('/login', methods = ['POST'], content_types=['application/json'], cors = True)
def login():
    try:
        jbody = app.current_request.json_body
        if 'email' in jbody and 'password' in jbody:
            table = dynamo.Table(CV_USR_TBL)
            response = table.get_item(Key = {'email': jbody['email']})
            if 'Item' in response:
                if response['Item']['password'] == hashlib.md5(jbody['password'].encode()).hexdigest():
                    token = jwt.encode({'email': response['Item']['email'], 'username': response['Item']['username']},
                                       HMAC_PASSWORD_2, algorithm='HS256')
                    return {"token": token.decode('utf-8')}
                else:
                    return UnauthorizedError("Invalid Credentials")
            else:
                return UnauthorizedError("Invalid Credentials")
        else:
            return BadRequestError("Inaccessible Fields")
    except Exception as e:
        return BadRequestError(str(e))


@app.route('/delete_user/{email}', methods=['DELETE'], cors = True)
def delete_user(email):
    try:
        hello = dict(app.current_request.headers)
        if 'authorization' in hello:
            token = hello.get('authorization')
            if token == 'admin' or token == 'staff':
                table = dynamo.Table(CV_USR_TBL)
                resp = table.delete_item(Key={
                    'email': email
                })
                if 'Error' in resp:
                    return BadRequestError("Unable to delete ")
                else:
                    return {'success': 'User with email: {} deleted'.format(email)}
            else:
                return UnauthorizedError('You are not allowed to execute this function')
        else:
            return UnauthorizedError("There's not token in your Request")
    except Exception as e:
        return BadRequestError(e)


def _get_parts():
    rfile = BytesIO(app.current_request.raw_body)
    content_type = app.current_request.headers['content-type']
    _, parameters = cgi.parse_header(content_type)
    parameters['boundary'] = parameters['boundary'].encode('utf-8')
    parsed = cgi.parse_multipart(rfile, parameters)
    return parsed


@app.route('/upload', methods=['POST'], content_types=['multipart/form-data'], cors = True)
def upload():
    try:
        hello = dict(app.current_request.headers)
        if 'authorization' in hello:
            decoded = jwt.decode(str(hello['authorization']), HMAC_PASSWORD_2, algorithms=['HS256'])
            print("decoded", decoded)
            details = is_valid_jwt(decoded)
        s3 = boto3.client('s3')
        files = _get_parts()
        try:
            for k, v in files.items():
                file_key = '{}.xml'.format(str(uuid4()))
                s3.upload_fileobj(BytesIO(v[0]), CV_BUCKET, file_key)

            table = dynamo.Table(CV_TBL)
            table.put_item(
                Item={
                    'filename': file_key,
                    'email': details[0]['email'],
                    'username': details[0]['username']
                }
            )
            sleep(2)
            return {'uploaded': True}
        except Exception as e:
            print(e)
            return BadRequestError(e)
    except Exception as e:
        raise BadRequestError(e)