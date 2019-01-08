import boto3
from faker import Faker
from huepy import *
from time import sleep
import sys
import hashlib

def run_fake_cards(table_name):
    fake = Faker()
    dynamo = boto3.resource('dynamodb')
    pci_table = dynamo.Table(table_name)

    for i in range(0, 50):
        name = fake.name()
        try:
            pci_table.put_item(Item = {
                'card_number': fake.credit_card_number(card_type=None),
                'full_name': name,
                'cvv': fake.credit_card_security_code(card_type=None),
                'expiration': fake.credit_card_expire(start = "now", end = "+5y", date_format="%m/%y")
            })
            print(good("Successfully generated card number for {}".format(name)))
            sleep(1)
        except Exception as e:
            print(bad(str(e)))

def run_fake_users(table_name):
    fake = Faker()
    dynamo = boto3.resource('dynamodb')
    pci_table = dynamo.Table(table_name)

    for i in range(0, 50):
        fname = fake.first_name()
        lname = fake.last_name()
        try:
            pci_table.put_item(Item={
                'email': fake.safe_email(),
                'first_name': fname,
                'last_name': lname,
                'username': fake.user_name(),
                'password': hashlib.md5(str.encode(fake.password())).hexdigest()
            })
            print(good("Successfully generated User Information for {} {}".format(fname, lname)))
            sleep(1)
        except Exception as e:
            print(bad(str(e)))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(bad('Please provide the table_name and action'))
        sys.exit(1)
    else:
        if sys.argv[1] == 'users':
            run_fake_users(sys.argv[2])
        elif sys.argv[1] == 'cards':
            run_fake_cards(sys.argv[2])
        else:
            print(bad("Only options are 'users' and 'cards'. None of that found"))
            sys.exit(1)

