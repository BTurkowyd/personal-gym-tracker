-- Staging model for workouts
-- Cleans and standardizes workout data from the Glue table

{{ config(
    materialized='view'
) }}

with source as (
    select * from {{ source('gym_tracker', 'workouts') }}
),

cleaned as (
    select
        id as workout_id,
        name as workout_name,
        index as workout_index,
        from_unixtime(start_time) as workout_start_datetime,
        from_unixtime(end_time) as workout_end_datetime,
        date(from_unixtime(start_time)) as workout_date,
        round(cast((end_time - start_time) as double) / 60.0, 2) as workout_duration_minutes,
        nth_workout,
        round(estimated_volume_kg, 2) as estimated_volume_kg,
        comment_count,
        routine_id,
        created_at,
        updated_at
    from source
)

select * from cleaned
