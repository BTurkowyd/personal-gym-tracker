-- Workout summary with aggregated metrics
-- Provides a complete view of each workout with calculated statistics

{{ config(
    materialized='view'
) }}

with workouts as (
    select * from {{ ref('stg_workouts') }}
),

exercises as (
    select * from {{ ref('stg_exercises') }}
),

sets as (
    select * from {{ ref('stg_sets') }}
),

workout_stats as (
    select
        s.workout_id,
        count(distinct s.exercise_id) as total_exercises,
        count(s.set_id) as total_sets,
        round(sum(s.set_volume_kg), 2) as total_volume_kg,
        round(avg(s.weight_kg), 2) as avg_weight_kg,
        round(max(s.weight_kg), 2) as max_weight_kg,
        sum(s.reps) as total_reps,
        round(avg(s.rate_of_perceived_exertion), 2) as avg_rpe
    from sets s
    group by s.workout_id
),

muscle_groups as (
    select
        e.workout_id,
        array_agg(distinct e.muscle_group) as muscle_groups_trained
    from exercises e
    where e.muscle_group is not null
    group by e.workout_id
)

select
    w.workout_id,
    w.workout_name,
    w.workout_date,
    w.workout_start_datetime,
    w.workout_end_datetime,
    w.workout_duration_minutes,
    w.nth_workout,
    w.estimated_volume_kg,
    ws.total_exercises,
    ws.total_sets,
    ws.total_volume_kg,
    ws.avg_weight_kg,
    ws.max_weight_kg,
    ws.total_reps,
    ws.avg_rpe,
    mg.muscle_groups_trained
from workouts w
left join workout_stats ws on w.workout_id = ws.workout_id
left join muscle_groups mg on w.workout_id = mg.workout_id
