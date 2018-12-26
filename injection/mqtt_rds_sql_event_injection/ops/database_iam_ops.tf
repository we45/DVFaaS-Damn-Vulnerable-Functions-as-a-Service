//resource "random_string" "db_password" {
//  length = 15
//  special = false
//}
//
//variable "vpc_cidr" {
//  default = "172.16.0.0/24"
//}
//
//variable "vpc_cidr_2" {
//  default = "172.17.0.0/24"
//}
//
//resource "aws_vpc" "stack-example-vpc" {
//  cidr_block = "${var.vpc_cidr}"
//  enable_dns_support = true
//  enable_dns_hostnames = true
//
//  tags {
//    Name = "stack-example-vpc"
//  }
//}
//
//resource "aws_subnet" "subnet_1" {
//  cidr_block = "${var.vpc_cidr}"
//  availability_zone = "us-east-1a"
//  vpc_id = "${aws_vpc.stack-example-vpc.id}"
//}
//
//resource "aws_subnet" "subnet_2" {
//  availability_zone = "us-east-1b"
//  cidr_block = "${var.vpc_cidr_2}"
//  vpc_id = "${aws_vpc.stack-example-vpc.id}"
//}
//
//resource "aws_security_group" "default" {
//  name        = "main_rds_sg"
//  description = "Allow all inbound traffic"
//  vpc_id      = "${aws_vpc.stack-example-vpc.id}"
//
//  ingress {
//    from_port   = 3306
//    to_port     = 3306
//    protocol    = "TCP"
//    cidr_blocks = ["0.0.0.0/0"]
//  }
//
//  egress {
//    from_port   = 0
//    to_port     = 0
//    protocol    = "-1"
//    cidr_blocks = ["0.0.0.0/0"]
//  }
//
//  tags {
//    Name = "RDS Security Group"
//  }
//}
//
//resource "aws_db_subnet_group" "default" {
//  name = "main_subnet_group"
//  description = "Main Group of Subnets"
//  subnet_ids = ["${aws_subnet.subnet_1.id}", "${aws_subnet.subnet_2.id}"]
//}
//
//resource "aws_db_instance" "crypto-db" {
//  depends_on = ["aws_security_group.default"]
//  instance_class = "db.t2.micro"
//  allocated_storage = 20
//  storage_type = "gp2"
//  engine = "mysql"
//  engine_version = "5.7"
//  name = "cryptodb"
//  username = "cryptesh"
//  password = "${random_string.db_password.result}"
//  publicly_accessible = true
//  vpc_security_group_ids = ["${aws_security_group.default.id}"]
//  skip_final_snapshot = true
//  final_snapshot_identifier = "Ignore"
//  db_subnet_group_name = "${aws_db_subnet_group.default.id}"
//}
//
//resource "local_file" "password_file" {
//  filename = "../pwd.json"
//  content = "{\"username\":\"cryptesh\", \"password\": \"${random_string.db_password.result}\"}"
//}
