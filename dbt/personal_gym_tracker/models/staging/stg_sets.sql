-- Staging model for sets
-- Cleans and standardizes set data from the Glue table

{{ config(
    materialized='view'
) }}

with source as (
    select * from {{ source('gym_tracker', 'sets') }}
),

cleaned as (
    select
        id as set_id,
        workout_id,
        exercise_id,
        index as set_order,
        reps,
        round(weight_kg, 2) as weight_kg,
        round(distance_meters, 2) as distance_meters,
        duration_seconds,
        round(rpe, 2) as rate_of_perceived_exertion,
        indicator as set_type,
        -- Calculate volume (weight * reps)
        round(coalesce(weight_kg * reps, 0.0), 2) as set_volume_kg
    from source
)

select * from cleaned
