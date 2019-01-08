resource "aws_iam_role_policy" "yaml-table-policy" {
  role = "${aws_iam_role.yaml-table-role.id}"
  policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
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

resource "aws_iam_role" "yaml-table-role" {
  name = "yaml_table_role"
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

output "iam_role_name" {
  value = "ARN: ${aws_iam_role.yaml-table-role.arn}"
}