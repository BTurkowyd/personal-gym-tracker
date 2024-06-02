resource "aws_glue_catalog_table" "users_table" {

  database_name = aws_athena_database.athena_workouts_database.name
  name          = "users_${var.caller_identity_id}"
  table_type = "EXTERNAL_TABLE"

  storage_descriptor {
    location = "s3://${var.data_bucket}/sorted_workouts"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                 = "users_${var.caller_identity_id}"
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
    }

    columns {
      name = "user_id"
      type = "string"
    }
    columns {
      name = "username"
      type = "string"
    }
    columns {
      name = "profile_image"
      type = "string"
    }
    columns {
      name = "verified"
      type = "boolean"
    }
  }
}