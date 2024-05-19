resource "aws_dynamodb_table" "workouts_table" {
  name = "WorkoutsTable-${random_id.dynamodb_suffix.b64_url}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "index"

  attribute {
    name = "index"
    type = "S"
  }
  attribute {
    name = "workout_day"
    type = "S"
  }

  global_secondary_index {
    hash_key        = "workout_day"
    name            = "WorkoutsTableWorkoutsDayGSI-${random_id.dynamodb_suffix.b64_url}"
    projection_type = "ALL"
  }
}

resource "random_id" "dynamodb_suffix" {
  byte_length = 16
}