# DynamoDB table for storing workout metadata.
resource "aws_dynamodb_table" "workouts_table" {
  name = "WorkoutsTable-${random_id.dynamodb_suffix.b64_url}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "index"

  # Primary key: index (string)
  attribute {
    name = "index"
    type = "S"
  }
  # Attribute for workout day (used in GSI).
  attribute {
    name = "workout_day"
    type = "S"
  }

  # Global secondary index for querying by workout day.
  global_secondary_index {
    hash_key        = "workout_day"
    name            = "WorkoutsTableWorkoutsDayGSI-${random_id.dynamodb_suffix.b64_url}"
    projection_type = "ALL"
  }
}

# Random suffix for DynamoDB table name uniqueness.
resource "random_id" "dynamodb_suffix" {
  byte_length = 16
}