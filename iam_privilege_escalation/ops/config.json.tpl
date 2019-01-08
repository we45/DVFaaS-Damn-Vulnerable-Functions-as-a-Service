{
  "version": "2.0",
  "app_name": "bad-dynamo-search",
  "stages": {
    "dev": {
      "api_gateway_stage": "api",
      "manage_iam_role": false,
      "iam_role_arn": "${ROLE_NAME}",
      "environment_variables": {
        "TRAINING_BUCKET": "${TRAINING_BUCKET}",
        "USER_TABLE": "${USER_TABLE}",
        "CV_TABLE": "${CV_TABLE}",
        "PCI_TABLE": "${PCI_TABLE}"
      }
    }
  }
}
