## XML External Entities with Event Injection

This is an XML External Entity Injection that is triggered through an Event Injection Attack.

* In this attack, the attacker uploads an XML file through a function to an S3 bucket.
* A Function is triggered based on the `objectCreate` event in S3 (post upload)
* The function parses the XML file with a vulnerable XML parser, triggering the XXE

### Setup - Infrastructure
* If you run the setup for the IAM Privilege Escalation exercise before this, you are done. The same infrastructure is being used for this lab
* Please ensure you copy the generated `config.json` in the `ops` directory of `iam_privilege_escalation` to the `.chalice` directory within `xxe-example`

### Setup - Function
* In the `xxe-example` directory, run `chalice deploy` to deploy the function to AWS Lambda

```
Creating deployment package.
Updating lambda function: dvfaas-XXXX
Updating lambda function: dvfaas-xxxx
Updating rest API
Resources deployed:
  - Lambda ARN: arn:aws:lambda:us-east-1:112222211:function:dvfaas-xxxx
  - Lambda ARN: arn:aws:lambda:us-east-1:112222211:function:dvfaas-xxxx
  - Rest API URL: https://xxxx.execute-api.us-east-1.amazonaws.com/api/

```

### Running the Lab
* You will need to authenticate and obtain a Authorization Token before you run the lab. For that, you'll have to sign up first

    ```
    http POST https://xxxxxx.execute-api.us-east-1.amazonaws.com/api/signup/
    username=someusername password=somepass first_name=firstname last_name=lastname email=some@email.com
    ```

* Next, please authenticate with the email and password provided during signup

    ```
    http POST https://XXXXXX.execute-api.us-east-1.amazonaws.com/api/login email=some@email.com password=somepass

    Response:

    {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImRpbmdkb25nQGV4YW1wbGUubmV0IiwidXNlcm5hbWUiOiJkaW5nIn0.l3qfroBO8DuwOEMgu6yTnrYwWiGlkBtrAg5LPH_W5mc"
    }
    ```

    You'll have to use this token in the request to upload the XML file

* Next, you'll have to upload a (malicious) XML file to the S3 bucket with the token

**You can find the malicious xml file [here](malicious-xml.xml)**

    ```
    http --form POST https://XXXX.execute-api.us-east-1.amazonaws.com/api/upload file@malicious-xml.xml
    ```

* Once uploaded, you should see that the file has uploaded. Subsequently, the function should have triggered. To see if it has worked,
you can browse to your Cloudwatch Logs in AWS Console. And under the `/aws/lambda/dvfaas-xxe-dev-cv_event_handler` log group, where you can see the executed XXE attack

![Cloudwatch XXE](img/cloudwatch_xxe.png)
