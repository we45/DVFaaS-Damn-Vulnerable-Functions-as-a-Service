resource "aws_s3_bucket" "logging_bucket" {
  bucket = "logging_bucket"
  acl    = "log-delivery-write"
}

resource "aws_s3_bucket" "training_bucket" {
  bucket = "training-cv-uploader"
  logging {
    target_bucket = "${aws_s3_bucket.logging_bucket.id}"
    target_prefix = "log/"
  }
}

resource "aws_dynamodb_table" "user_table" {
  name = "cv_users"
  hash_key = "email"
  read_capacity = 100
  write_capacity = 100

  attribute {
    name = "email"
    type = "S"
  }
}

resource "aws_dynamodb_table" "data_table" {
  hash_key = "filename"
  name = "cv_data"
  read_capacity = 100
  write_capacity = 100

  "attribute" {
    name = "filename"
    type = "S"
  }
}

resource "aws_dynamodb_table" "pci_table" {
  name = "payment-cards"
  hash_key = "card_number"
  read_capacity = 100
  write_capacity = 100

  "attribute" {
    name = "card_number"
    type = "S"
  }
}
