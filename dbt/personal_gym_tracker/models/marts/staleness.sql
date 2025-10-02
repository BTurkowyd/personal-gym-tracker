-- Staleness mart: exercises and muscle groups not trained recently

{{ config(materialized='view') }}

with exercises as (
    select * from {{ ref('stg_exercises') }}
),
workouts as (
    select * from {{ ref('stg_workouts') }}
),

exercises_with_date as (
    select
        e.exercise_name,
        e.muscle_group,
        w.workout_date
    from exercises e
    inner join workouts w on e.workout_id = w.workout_id
),

last_trained as (
    select
        exercise_name,
        muscle_group,
        max(workout_date) as last_trained_date
    from exercises_with_date
    group by exercise_name, muscle_group
),

stale_exercises as (
    select
        exercise_name,
        muscle_group,
        last_trained_date,
        date_diff('day', last_trained_date, current_date) as days_since_trained
    from last_trained
    where date_diff('day', last_trained_date, current_date) > 14 -- configurable threshold
)

select * from stale_exercises
order by days_since_trained desc
