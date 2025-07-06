// Glue Catalog Table for workouts data.
// This table is external and points to data stored in S3 in the 'sorted_workouts' folder.
resource "aws_glue_catalog_table" "workouts_table" {
  database_name = aws_athena_database.athena_workouts_database.name // Reference to Athena DB
  name          = "workouts_${var.caller_identity_id}"              // Unique table name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.data_bucket}/sorted_workouts" // S3 location for data
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "users_${var.caller_identity_id}"
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
    }

    // Table columns definition for workouts data
    columns {
      name = "id"
      type = "string"
      comment = "Unique identifier for the workout"
    }
    columns {
      name = "short_id"
      type = "string"
      comment = "Short identifier for the workout"
    }
    columns {
      name = "index"
      type = "bigint"
      comment = "Index of the workout"
    }
    columns {
      name = "name"
      type = "string"
      comment = "Name of the workout"
    }
    columns {
      name = "description"
      type = "string"
      comment = "Description of the workout"
    }
    columns {
      name = "start_time"
      type = "timestamp"
      comment = "Start time of the workout"
    }
    columns {
      name = "end_time"
      type = "timestamp"
      comment = "End time of the workout"
    }
    columns {
      name = "created_at"
      type = "string"
      comment = "Creation time of the workout"
    }
    columns {
      name = "updated_at"
      type = "string"
      comment = "Last update time of the workout"
    }
    columns {
      name = "apple_watch"
      type = "boolean"
      comment = "Indicates if the workout was recorded on an Apple Watch"
    }
    columns {
      name = "wearos_watch"
      type = "boolean"
      comment = "Indicates if the workout was recorded on a Wear OS watch"
    }
    columns {
      name = "user_id"
      type = "string"
      comment = "Unique identifier for the user"
    }
    columns {
      name = "username"
      type = "string"
      comment = "Username of the user"
    }
    columns {
      name = "profile_image"
      type = "string"
      comment = "Profile image URL of the user"
    }
    columns {
      name = "verified"
      type = "boolean"
      comment = "Indicates if the user is verified"
    }
    columns {
      name = "nth_workout"
      type = "int"
      comment = "Indicates the nth workout for the user"
    }
    columns {
      name = "like_count"
      type = "int"
      comment = "Number of likes for the workout"
    }
    columns {
      name = "is_liked_by_user"
      type = "boolean"
      comment = "Indicates if the workout is liked by the user"
    }
    columns {
      name = "is_private"
      type = "boolean"
      comment = "Indicates if the workout is private"
    }
    columns {
      name = "like_images"
      type = "array<string>"
      comment = "List of image URLs for likes"
    }
    columns {
      name = "comments"
      type = "array<string>"
      comment = "List of comments for the workout"
    }
    columns {
      name = "comment_count"
      type = "int"
      comment = "Number of comments for the workout"
    }
    columns {
      name = "media"
      type = "array<string>"
      comment = "List of media URLs for the workout"
    }
    columns {
      name = "image_urls"
      type = "array<string>"
      comment = "List of image URLs for the workout"
    }
    columns {
      name = "exercises"
      type = "array<struct<id:string,url:string,sets:array<struct<id:string,prs:array<string>,rpe:double,reps:int,index:int,indicator:string,weight_kg:double,distance_meters:double,personalRecords:array<string>,duration_seconds:int>>,notes:string,title:string,de_title:string,es_title:string,fr_title:string,it_title:string,ja_title:string,ko_title:string,priority:int,pt_title:string,ru_title:string,tr_title:string,media_type:string,superset_id:string,zh_cn_title:string,zh_tw_title:string,muscle_group:string,rest_seconds:int,exercise_type:string,other_muscles:array<string>,thumbnail_url:string,equipment_category:string,exercise_template_id:string,volume_doubling_enabled:boolean,custom_exercise_image_url:string,custom_exercise_image_thumbnail_url:string>>"
      comment = "List of exercises in the workout, each with its own details"
    }
  }
}

resource "aws_glue_catalog_table" "workouts_table_parquet" {
  database_name = aws_athena_database.athena_workouts_database.name
  name          = "workouts_${var.caller_identity_id}_parquet"
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.data_bucket}/sorted_workouts_parquet"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "id"
      type = "string"
    }
    columns {
      name = "name"
      type = "string"
    }
    columns {
      name = "index"
      type = "bigint"
    }
    columns {
      name = "user_id"
      type = "string"
    }
    columns {
      name = "end_time"
      type = "bigint"
    }
    columns {
      name = "username"
      type = "string"
    }
    columns {
      name = "created_at"
      type = "string"
    }
    columns {
      name = "routine_id"
      type = "string"
    }
    columns {
      name = "start_time"
      type = "bigint"
    }
    columns {
      name = "updated_at"
      type = "string"
    }
    columns {
      name = "nth_workout"
      type = "int"
    }
    columns {
      name = "comment_count"
      type = "int"
    }
    columns {
      name = "estimated_volume_kg"
      type = "double"
    }
    columns {
      name = "exercise_id"
      type = "string"
    }
    columns {
      name = "exercise_title"
      type = "string"
    }
    columns {
      name = "exercise_priority"
      type = "int"
    }
    columns {
      name = "exercise_muscle_group"
      type = "string"
    }
    columns {
      name = "exercise_rest_seconds"
      type = "int"
    }
    columns {
      name = "exercise_exercise_type"
      type = "string"
    }
    columns {
      name = "exercise_equipment_category"
      type = "string"
    }
    columns {
      name = "exercise_exercise_template_id"
      type = "string"
    }
    columns {
      name = "set_id"
      type = "string"
    }
    columns {
      name = "set_rpe"
      type = "double"
    }
    columns {
      name = "set_reps"
      type = "int"
    }
    columns {
      name = "set_index"
      type = "int"
    }
    columns {
      name = "set_indicator"
      type = "string"
    }
    columns {
      name = "set_weight_kg"
      type = "double"
    }
    columns {
      name = "set_distance_meters"
      type = "double"
    }
    columns {
      name = "set_duration_seconds"
      type = "int"
    }
  }
}