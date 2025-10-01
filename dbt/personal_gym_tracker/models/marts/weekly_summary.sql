-- Weekly workout aggregates
-- Provides weekly summary statistics for tracking progress over time

{{ config(
    materialized='view'
) }}

with workouts as (
    select * from {{ ref('stg_workouts') }}
),

sets as (
    select * from {{ ref('stg_sets') }}
),

weekly_workouts as (
    select
        date_trunc('week', w.workout_date) as week_start_date,
        count(distinct w.workout_id) as workouts_per_week,
        round(sum(w.workout_duration_minutes), 2) as total_workout_time_minutes,
        round(avg(w.workout_duration_minutes), 2) as avg_workout_duration_minutes,
        round(sum(w.estimated_volume_kg), 2) as total_estimated_volume_kg
    from workouts w
    group by date_trunc('week', w.workout_date)
),

weekly_sets as (
    select
        date_trunc('week', w.workout_date) as week_start_date,
        count(s.set_id) as total_sets,
        round(sum(s.set_volume_kg), 2) as total_volume_kg,
        round(avg(s.weight_kg), 2) as avg_weight_kg,
        sum(s.reps) as total_reps
    from sets s
    inner join workouts w on s.workout_id = w.workout_id
    group by date_trunc('week', w.workout_date)
)

select
    ww.week_start_date,
    date_add('day', 6, ww.week_start_date) as week_end_date,
    ww.workouts_per_week,
    ww.total_workout_time_minutes,
    ww.avg_workout_duration_minutes,
    ws.total_sets,
    ws.total_volume_kg,
    ws.avg_weight_kg,
    ws.total_reps,
    ww.total_estimated_volume_kg
from weekly_workouts ww
left join weekly_sets ws on ww.week_start_date = ws.week_start_date
order by ww.week_start_date desc
