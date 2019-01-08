resource "random_string" "rando" {
  length = 10
  lower = true
  upper = false
  special = false
}

resource "aws_s3_bucket" "training_bucket" {
  bucket = "${random_string.rando.result}-training-cv-uploader"
}

resource "aws_dynamodb_table" "user_table" {
  name = "${random_string.rando.result}_cv_users"
  hash_key = "email"
  read_capacity = 5
  write_capacity = 5

  attribute {
    name = "email"
    type = "S"
  }
}

resource "aws_dynamodb_table" "data_table" {
  hash_key = "filename"
  name = "${random_string.rando.result}_cv_data"
  read_capacity = 5
  write_capacity = 5

  "attribute" {
    name = "filename"
    type = "S"
  }
}

resource "aws_dynamodb_table" "pci_table" {
  name = "${random_string.rando.result}-payment-cards"
  hash_key = "card_number"
  read_capacity = 6
  write_capacity = 6

  "attribute" {
    name = "card_number"
    type = "S"
  }

  provisioner "local-exec" {
    # replace this with your python virtualenv or python path as required
    command = <<EOT
        /Users/abhaybhargav/.local/share/virtualenvs/dvfaas-PgKv6mNG/bin/python create_dummies.py cards ${random_string.rando.result}-payment-cards &&
        /Users/abhaybhargav/.local/share/virtualenvs/dvfaas-PgKv6mNG/bin/python create_dummies.py users ${aws_dynamodb_table.user_table.name}
    EOT
  }
}

resource "aws_iam_role_policy" "bad-role-policy" {
  role = "${aws_iam_role.tes_role.id}"
  policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
	{
		"Action": [
          "dynamodb:*",
          "s3:*"
		],
		"Effect": "Allow",
		"Resource": "*"
	},
    {
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
		],
		"Effect": "Allow",
		"Resource": "arn:aws:logs:*:*:*"
	}
	]
}
EOF
}

resource "aws_iam_role" "tes_role" {
  name = "${random_string.rando.result}_bad_dynamodb_policy"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

data "template_file" "config_chalice" {
  template = "${file("config.json.tpl")}"
  vars {
    ROLE_NAME = "${aws_iam_role.tes_role.arn}"
    TRAINING_BUCKET = "${aws_s3_bucket.training_bucket.bucket}"
    USER_TABLE = "${aws_dynamodb_table.user_table.name}"
    CV_TABLE = "${aws_dynamodb_table.data_table.name}"
    PCI_TABLE = "${aws_dynamodb_table.pci_table.name}"
  }
}

resource "local_file" "variables_json" {
  filename = "config.json"
  content = "${data.template_file.config_chalice.rendered}"
}