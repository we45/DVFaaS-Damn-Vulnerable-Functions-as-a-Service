from chalice import Chalice, BadRequestError
import boto3

app = Chalice(app_name='dvfaas-bad-dynamo-search')

@app.route('/search', methods=['POST'], content_types=['application/json'], cors = True)
def bad_search():
    try:
        jbody = app.current_request.json_body
        if isinstance(jbody, dict):
            if 'db' in jbody and 'search_term' in jbody and 'search_operator' in jbody \
                    and 'search_field' in jbody:
                db = boto3.client('dynamodb')
                response = db.scan(TableName=jbody['db'], Select='ALL_ATTRIBUTES', ScanFilter={
                    jbody['search_field']: {"AttributeValueList": [{"S": jbody['search_term']}],
                                            "ComparisonOperator": jbody['search_operator']}
                })
                if 'Items' in response:
                    return {"search_results": response['Items']}
                else:
                    return {"search_results": None}
            else:
                return BadRequestError("All parameters are required to complete the search")
        else:
            return BadRequestError("Seems to be a wrong content type")
    except Exception as e:
        return {"error": str(e)}