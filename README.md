# DVFaaS - Damn Vulnerable Functions as a Service

> A Project that you can deploy and run a bunch of 'orribly insecure functions on AWS Lambda

### Objective and Audiences
This project is great for you, if:
* You want to learn about security flaws with serverless apps, specifically FaaS implementations.

This project is not for you, if:
* You don't want to deploy (and run) your own functions. The idea here is for you to learn by doing.

#### Please note:
* The functions are targeted to be deployed in AWS Lambda. But the principles and concepts apply across the board
* Most of the functions are in Python, specifically in a framework called `chalice` (meant for python on AWS Lambda). Deployment of these functions to your lambda environment is reasonably simple
* Ultimately the project maps to the OWASP Serverless Top 10, found [here](https://www.owasp.org/index.php/OWASP_Serverless_Top_10_Project), but some examples may vary
* The ops (deployment) for this project is largely done with Terraform. Please find docs [here](https://www.terraform.io/docs/providers/aws/)
* Each example has a README, which has installation instructions, etc. In many cases, the deployment for multiple examples ove


### Requirements
#### Code
* Python 3.6
* Pipenv (dependency management)
* Chalice
* PyYAML

#### AWS Resources
* RDS => MySQL (Free Tier eligible)
* DynamoDB (Free Tier Eligible)
* Amazon SNS (Pub/Sub for Topics)
* Amazon Lambda, y'know....for functions
* Amazon Cloudwatch Logs



