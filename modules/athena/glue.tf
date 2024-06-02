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
    columns {
        name = "exercises"
        type = "array<struct<id:string,title:string,es_title:string,de_title:string,fr_title:string,it_title:string,pt_title:string,ko_title:string,ja_title:string,tr_title:string,ru_title:string,zh_cn_title:string,zh_tw_title:string,superset_id:string,rest_seconds:int,notes:string,exercise_template_id:string,url:string,exercise_type:string,equipment_category:string,media_type:string,custom_exercise_image_url:string,custom_exercise_image_thumbnail_url:string,thumbnail_url:string,muscle_group:string,other_muscles:array<string>,priority:int,sets:array<struct<id:string,index:int,indicator:string,weight_kg:double,reps:int,distance_meters:int,duration_seconds:int,rpe:double,prs:array<struct<type:string,value:double>>,personalRecords:array<struct<type:string,value:double>>>>>>"
      }
  }
}