resource "aws_dynamodb_table" "workouts_table" {
  name = "WorkoutsTable-${random_id.dynamodb_suffix.b64_url}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "index"

  attribute {
    name = "index"
    type = "N"
  }
}

resource "random_id" "dynamodb_suffix" {
  byte_length = 16
}