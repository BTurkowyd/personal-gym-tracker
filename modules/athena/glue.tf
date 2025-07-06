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
      type = "timestamp"
    }
    columns {
      name = "end_time"
      type = "timestamp"
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
    columns {
      name = "exercises"
      type = "array<struct<id:string,url:string,sets:array<struct<id:string,prs:array<string>,rpe:double,reps:int,index:int,indicator:string,weight_kg:double,distance_meters:double,personalRecords:array<string>,duration_seconds:int>>,notes:string,title:string,de_title:string,es_title:string,fr_title:string,it_title:string,ja_title:string,ko_title:string,priority:int,pt_title:string,ru_title:string,tr_title:string,media_type:string,superset_id:string,zh_cn_title:string,zh_tw_title:string,muscle_group:string,rest_seconds:int,exercise_type:string,other_muscles:array<string>,thumbnail_url:string,equipment_category:string,exercise_template_id:string,volume_doubling_enabled:boolean,custom_exercise_image_url:string,custom_exercise_image_thumbnail_url:string>>"
    }
  }
}