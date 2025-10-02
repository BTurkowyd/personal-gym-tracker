-- Staging model for performed exercises
-- Cleans and standardizes exercise data from the Glue table

{{ config(
    materialized='view'
) }}

with source as (
    select * from {{ source('gym_tracker', 'performed_exercises') }}
),

cleaned as (
    select
        id as exercise_id,
        workout_id,
        title as exercise_name,
        index as exercise_order,
        exercise_type,
        equipment_category,
        muscle_group,
        exercise_template_id,
        priority,
        created_at,
        updated_at
    from source
)

select * from cleaned
