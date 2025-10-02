-- Muscle group training frequency
-- Shows how often each muscle group is trained

{{ config(
    materialized='view'
) }}

with exercises as (
    select * from {{ ref('stg_exercises') }}
),

workouts as (
    select * from {{ ref('stg_workouts') }}
),

sets as (
    select * from {{ ref('stg_sets') }}
),

muscle_group_workouts as (
    select
        e.muscle_group,
        w.workout_date,
        w.workout_id,
        count(distinct e.exercise_id) as exercises_performed,
        count(s.set_id) as total_sets,
        round(sum(s.set_volume_kg), 2) as total_volume_kg
    from exercises e
    inner join workouts w on e.workout_id = w.workout_id
    left join sets s on e.exercise_id = s.exercise_id
    where e.muscle_group is not null
    group by e.muscle_group, w.workout_date, w.workout_id
),

muscle_group_stats as (
    select
        muscle_group,
        count(distinct workout_id) as times_trained,
        count(distinct workout_date) as days_trained,
        sum(exercises_performed) as total_exercises,
        sum(total_sets) as total_sets,
        round(sum(total_volume_kg), 2) as total_volume_kg,
        round(avg(total_volume_kg), 2) as avg_volume_per_session,
        max(workout_date) as last_trained_date,
        min(workout_date) as first_trained_date
    from muscle_group_workouts
    group by muscle_group
)

select
    muscle_group,
    times_trained,
    days_trained,
    total_exercises,
    total_sets,
    total_volume_kg,
    avg_volume_per_session,
    last_trained_date,
    first_trained_date,
    date_diff('day', last_trained_date, current_date) as days_since_last_trained
from muscle_group_stats
order by times_trained desc
