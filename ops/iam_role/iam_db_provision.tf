resource "aws_iam_role_policy" "bad-role-policy" {
  role = "${aws_iam_role.tes_role.id}"
  policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [{
		"Action": [
          "dynamodb:*",
          "s3:*"
		],
		"Effect": "Allow",
		"Resource": "*"
	}]
}
EOF
}

resource "aws_iam_role" "tes_role" {
  name = "bad_dynamodb_policy"
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