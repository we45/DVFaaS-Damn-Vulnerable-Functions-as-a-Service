from chalice import Chalice
import yaml
from io import BytesIO
import cgi

app = Chalice(app_name='dvfaas-insecure-deserialization')


def _get_parts():
    rfile = BytesIO(app.current_request.raw_body)
    content_type = app.current_request.headers['content-type']
    _, parameters = cgi.parse_header(content_type)
    parameters['boundary'] = parameters['boundary'].encode('utf-8')
    parsed = cgi.parse_multipart(rfile, parameters)
    return parsed


@app.route('/test')
def test_route():
    print('Test is working')
    return {'success': 'test'}

@app.route('/yaml_upload/{email}', methods = ['POST'], content_types=['multipart/form-data'], cors = True)
def index(email):
    files = _get_parts()
    try:
        for k, v in files.items():
            yaml_content = yaml.load(BytesIO(v[0]))
            return str(yaml_content)
    except Exception as e:
        return {"error": str(e)}

