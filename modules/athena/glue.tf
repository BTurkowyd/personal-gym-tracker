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
      comment = "Start time of the workout. Can be used to determine when the workout began"
    }
    columns {
      name = "end_time"
      type = "timestamp"
      comment = "End time of the workout. Can be used to determine when the workout ended"
    }
    columns {
      name = "created_at"
      type = "string"
      comment = "Creation time of the workout. Can be used to determine when the record was created"
    }
    columns {
      name = "updated_at"
      type = "string"
      comment = "Last update time of the workout. Can be used to determine when the record was last updated"
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
      comment = "Indicates the nth workout for the user. This can be used to track the user's workout history"
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


// Glue Table for workouts.parquet
resource "aws_glue_catalog_table" "workouts_table_parquet" {
  database_name = aws_athena_database.athena_workouts_database.name
  name          = "workouts"
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.data_bucket}/sorted/workouts"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "id"
      type = "string"
      comment = "Unique identifier for the workout"
    }
    columns {
      name = "name"
      type = "string"
      comment = "Name of the workout"
    }
    columns {
      name = "index"
      type = "bigint"
      comment = "Index of the workout"
    }
    columns {
      name = "end_time"
      type = "bigint"
      comment = "End time of the workout. Can be used to determine when the workout ended"
    }
    columns {
      name = "created_at"
      type = "string"
      comment = "Creation time of the workout. Can be used to determine when the record was created"
    }
    columns {
      name = "routine_id"
      type = "string"
      comment = "Routine identifier (may be null)"
    }
    columns {
      name = "start_time"
      type = "bigint"
      comment = "Start time of the workout. Can be used to determine when the workout began"
    }
    columns {
      name = "updated_at"
      type = "string"
      comment = "Last update time of the workout. Can be used to determine when the record was last updated"
    }
    columns {
      name = "nth_workout"
      type = "bigint"
      comment = "The nth workout in the user's workout history. This can be used to track the user's workout progression"
    }
    columns {
      name = "comment_count"
      type = "bigint"
      comment = "Number of comments for the workout"
    }
    columns {
      name = "estimated_volume_kg"
      type = "double"
      comment = "Estimated volume of the workout in kg"
    }
  }
}

// Glue Table for performed_exercises.parquet
resource "aws_glue_catalog_table" "performed_exercises_table_parquet" {
  database_name = aws_athena_database.athena_workouts_database.name
  name          = "performed_exercises"
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.data_bucket}/sorted/exercises"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "id"
      type = "string"
      comment = "Unique identifier for the exercise. Uniquely identifies the exercise within the workout"
    }
    columns {
      name = "title"
      type = "string"
      comment = "Name of the exercise"
    }
    columns {
      name = "index"
      type = "bigint"
      comment = "Index of the exercise (may be null)"
    }
    columns {
      name = "workout_id"
      type = "string"
      comment = "Unique identifier for the workout. A foreign key to the workouts table (id)"
    }
    columns {
      name = "created_at"
      type = "string"
      comment = "Creation time (may be null)"
    }
    columns {
      name = "updated_at"
      type = "string"
      comment = "Last update time (may be null)"
    }
    columns {
      name = "exercise_type"
      type = "string"
      comment = "Type of the exercise"
    }
    columns {
      name = "equipment_category"
      type = "string"
      comment = "Type of equipment used for the exercise"
    }
    columns {
      name = "exercise_template_id"
      type = "string"
      comment = "Unique identifier for the exercise template"
    }
    columns {
      name = "priority"
      type = "bigint"
      comment = "Priority of the exercise"
    }
    columns {
      name = "muscle_group"
      type = "string"
      comment = "Muscle group or body part targeted by the exercise"
    }
  }
}

// Glue Table for sets.parquet
resource "aws_glue_catalog_table" "sets_table_parquet" {
  database_name = aws_athena_database.athena_workouts_database.name
  name          = "sets"
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.data_bucket}/sorted/sets"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "id"
      type = "string"
      comment = "Unique identifier for the set. Uniquely identifies the set within the workout"
    }
    columns {
      name = "rpe"
      type = "double"
      comment = "Rate of Perceived Exertion for the set"
    }
    columns {
      name = "reps"
      type = "bigint"
      comment = "Number of repetitions for the set"
    }
    columns {
      name = "index"
      type = "bigint"
      comment = "Index of the set within the exercise"
    }
    columns {
      name = "indicator"
      type = "string"
      comment = "Indicator for the set"
    }
    columns {
      name = "weight_kg"
      type = "double"
      comment = "Weight lifted for the set in kg"
    }
    columns {
      name = "distance_meters"
      type = "double"
      comment = "Distance covered during the set in meters"
    }
    columns {
      name = "duration_seconds"
      type = "bigint"
      comment = "Duration of the set in seconds"
    }
    columns {
      name = "exercise_id"
      type = "string"
      comment = "Unique identifier for the exercise. A foreign key to the exercises table (id)"
    }
    columns {
      name = "workout_id"
      type = "string"
      comment = "Unique identifier for the workout. A foreign key to the workouts table (id)"
    }
  }
}

resource "aws_glue_catalog_table" "exercise_catalog_table" {
  database_name = aws_athena_database.athena_workouts_database.name
  name          = "exercise_catalog"
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.data_bucket}/sorted/exercise_descriptions"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "title"
      type = "string"
      comment = "Title of the exercise"
    }
    columns {
      name = "equipment_category"
      type = "string"
      comment = "Category of equipment used for the exercise"
    }
    columns {
      name = "muscle_group"
      type = "string"
      comment = "Muscle group targeted by the exercise"
    }
    columns {
      name = "body_part"
      type = "string"
      comment = "Body part targeted by the exercise"
    }
    columns {
      name = "movement_type"
      type = "string"
      comment = "Type of movement involved in the exercise (e.g. compound, isolation)"
    }
  }

}