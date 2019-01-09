## Insecure Deserialization - Remote Code Execution

This attack/payload has been documented [here](https://twitter.com/abhaybhargav/status/1080034019230842880)

On reading, you'll see that its a NoSQL Injection attack that's predicated on using the `gt` operator. One of the main reasons that this attack is made possible, is because of badly configured IAM privileges

### Setup - Infrastructure

* This lab is pretty easy to deploy. Just cd into the `insecure-deserialization` directory and run `chalice deploy` which will deploy the function

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

### Exploit
* Once you are done with the deploy, you can use a HTTP Client or `httpie` to call the function

#### Genuine search with the REST API Function against the user database

* The function allows you to upload YAML files that are processed and further displayed as JSON as part of the response.
* The exploit leverages the function `yaml.load()` in python's `PyYaml` that deserializes python objects, thereby leading to Remote Code Execution
* You can initially upload a genuine YAML file to the endpoint

`http --form POST https://xxxx.execute-api.us-east-1.amazonaws.com/api/yaml_upload/someemail@example.com file@payload.yml`

The payload file that triggers RCE is in the `insecure-deserialization` directory. If you use that file, you'll find that it dumps all the
current env-vars loaded in the Lambda Function, including the `AWS-Access-Key-ID`, `secret` and `token` at the time