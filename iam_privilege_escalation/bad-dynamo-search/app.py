from chalice import Chalice

app = Chalice(app_name='bad-dynamo-search')

@app.route('/bad_dynamo_search', methods=['POST'], content_types=['application/json'], cors = True)
def bad_search():
    try:
        jbody = app.current_request.json_body
        if isinstance(jbody, dict):
            if jbody.has_key('db') and jbody.has_key('search_term') and jbody.has_key(
                    'search_operator') and jbody.has_key('search_field'):
                db = boto3.client('dynamodb')
                response = db.scan(TableName=jbody['db'], Select='ALL_ATTRIBUTES', ScanFilter={
                    jbody['search_field']: {"AttributeValueList": [{"S": jbody['search_term']}],
                                            "ComparisonOperator": jbody['search_operator']}
                })
                if response.has_key('Items'):
                    return {"search_results": response['Items']}
                else:
                    return {"search_results": None}
            else:
                return BadRequestError("All parameters are required to complete the search")
        else:
            return BadRequestError("Seems to be a wrong content type")
    except Exception as e:
        return BadRequestError(e.message)