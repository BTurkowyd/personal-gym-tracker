resource "aws_glue_catalog_table" "users_table" {
  # todo: this table will be completely changed
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

resource "aws_glue_catalog_table" "workouts_table" {
  database_name =aws_athena_database.athena_workouts_database.name
  name          = "workouts_${var.caller_identity_id}"
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
      name = "id"
      type = "string"
    }
    columns {
      name = "short_id"
      type = "string"
    }
    columns {
      name = "index"
      type = "bigint"
    }
    columns {
      name = "name"
      type = "string"
    }
    columns {
      name = "description"
      type = "string"
    }
    columns {
      name = "start_time"
      type = "bigint"
    }
    columns {
      name = "end_time"
      type = "bigint"
    }
    columns {
      name = "created_at"
      type = "string"
    }
    columns {
      name = "updated_at"
      type = "string"
    }
    columns {
      name = "apple_watch"
      type = "boolean"
    }
    columns {
      name = "wearos_watch"
      type = "boolean"
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
    columns {
      name = "nth_workout"
      type = "int"
    }
    columns {
      name = "like_count"
      type = "int"
    }
    columns {
      name = "is_liked_by_user"
      type = "boolean"
    }
    columns {
      name = "is_private"
      type = "boolean"
    }
    columns {
      name = "like_images"
      type = "array<string>"
    }
    columns {
      name = "comments"
      type = "array<string>"
    }
    columns {
      name = "comment_count"
      type = "int"
    }
    columns {
      name = "media"
      type = "array<string>"
    }
    columns {
      name = "image_urls"
      type = "array<string>"
    }
  }
}

resource "aws_glue_catalog_table" "exercises_table" {
  database_name = aws_athena_database.athena_workouts_database.name
  name          = "exercises_${var.caller_identity_id}"
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
      name = "id"
      type = "string"
    }
    columns {
      name = "title"
      type = "string"
    }
    columns {
      name = "es_title"
      type = "string"
    }
    columns {
      name = "de_title"
      type = "string"
    }
    columns {
      name = "fr_title"
      type = "string"
    }
    columns {
      name = "it_title"
      type = "string"
    }
    columns {
      name = "pt_title"
      type = "string"
    }
    columns {
      name = "ko_title"
      type = "string"
    }
    columns {
      name = "ja_title"
      type = "string"
    }
    columns {
      name = "tr_title"
      type = "string"
    }
    columns {
      name = "ru_title"
      type = "string"
    }
    columns {
      name = "zh_cn_title"
      type = "string"
    }
    columns {
      name = "zh_tw_title"
      type = "string"
    }
    columns {
      name = "superset_id"
      type = "string"
    }
    columns {
      name = "rest_seconds"
      type = "int"
    }
    columns {
      name = "notes"
      type = "string"
    }
    columns {
      name = "exercise_template_id"
      type = "string"
    }
    columns {
      name = "url"
      type = "string"
    }
    columns {
      name = "exercise_type"
      type = "string"
    }
    columns {
      name = "equipment_category"
      type = "string"
    }
    columns {
      name = "media_type"
      type = "string"
    }
    columns {
      name = "custom_exercise_image_url"
      type = "string"
    }
    columns {
      name = "custom_exercise_image_thumbnail_url"
      type = "string"
    }
    columns {
      name = "thumbnail_url"
      type = "string"
    }
    columns {
      name = "muscle_group"
      type = "string"
    }
    columns {
      name = "other_muscles"
      type = "array<string>"
    }
    columns {
      name = "priority"
      type = "int"
    }
  }
}

resource "aws_glue_catalog_table" "sets_table" {
  database_name = aws_athena_database.athena_workouts_database.name
  name          = "sets_${var.caller_identity_id}"
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
      name = "id"
      type = "string"
    }
    columns {
      name = "index"
      type = "int"
    }
    columns {
      name = "indicator"
      type = "string"
    }
    columns {
      name = "weight_kg"
      type = "double"
    }
    columns {
      name = "reps"
      type = "int"
    }
    columns {
      name = "distance_meters"
      type = "double"
    }
    columns {
      name = "duration_seconds"
      type = "int"
    }
    columns {
      name = "rpe"
      type = "int"
    }
    columns {
      name = "prs"
      type = "array<struct<type:string,value:double>>"
    }
  }
}