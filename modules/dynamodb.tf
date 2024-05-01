resource "aws_dynamodb_table" "workouts_table" {
  name = "WorkoutsTable-${random_id.dynamodb_suffix.b64_url}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "index"

  attribute {
    name = "index"
    type = "N"
  }
#   attribute {
#     name = "name"
#     type = "S"
#   }
#   attribute {
#     name = "routine_id"
#     type = "S"
#   }
#   attribute {
#     name = "id"
#     type = "S"
#   }
#   attribute {
#     name = "nth_workout"
#     type = "N"
#   }
#   attribute {
#     name = "start_time"
#     type = "N"
#   }
#   attribute {
#     name = "bucket_location"
#     type = "S"
#   }
}

resource "random_id" "dynamodb_suffix" {
  byte_length = 16
}