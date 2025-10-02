-- Exercise frequency and usage analysis
-- Shows most/least performed exercises, equipment usage patterns, and distribution

{{ config(
    materialized='view'
) }}

with exercises as (
    select * from {{ ref('stg_exercises') }}
),

sets as (
    select * from {{ ref('stg_sets') }}
),

workouts as (
    select * from {{ ref('stg_workouts') }}
),

exercise_stats as (
    select
        e.exercise_name,
        e.muscle_group,
        e.equipment_category,
        count(distinct e.workout_id) as times_performed,
        count(distinct w.workout_date) as days_performed,
        count(distinct e.exercise_id) as total_exercise_instances,
        count(s.set_id) as total_sets,
        sum(s.reps) as total_reps,
        round(sum(s.set_volume_kg), 2) as total_volume_kg,
        round(avg(s.weight_kg), 2) as avg_weight_kg,
        round(max(s.weight_kg), 2) as max_weight_kg,
        round(avg(s.rate_of_perceived_exertion), 2) as avg_rpe,
        -- Calculate average sets per performance
        round(cast(count(s.set_id) as double) / count(distinct e.exercise_id), 2) as avg_sets_per_performance,
        -- Calculate average reps per set
        round(cast(sum(s.reps) as double) / count(s.set_id), 2) as avg_reps_per_set,
        -- Get date ranges
        min(w.workout_date) as first_performed_date,
        max(w.workout_date) as last_performed_date,
        date_diff('day', max(w.workout_date), current_date) as days_since_last_performed
    from exercises e
    left join sets s on e.exercise_id = s.exercise_id
    inner join workouts w on e.workout_id = w.workout_id
    group by
        e.exercise_name,
        e.muscle_group,
        e.equipment_category
),

equipment_stats as (
    select
        equipment_category,
        count(distinct exercise_name) as unique_exercises,
        count(distinct exercise_id) as total_uses,
        sum(total_sets) as total_sets,
        round(sum(total_volume_kg), 2) as total_volume_kg
    from exercises e
    left join sets s on e.exercise_id = s.exercise_id
    where equipment_category is not null
    group by equipment_category
),

-- Add ranking for exercises
ranked_exercises as (
    select
        *,
        row_number() over (order by times_performed desc, total_volume_kg desc) as popularity_rank,
        row_number() over (partition by muscle_group order by times_performed desc) as muscle_group_rank
    from exercise_stats
)

select
    exercise_name,
    muscle_group,
    equipment_category,
    times_performed,
    days_performed,
    total_exercise_instances,
    total_sets,
    total_reps,
    total_volume_kg,
    avg_weight_kg,
    max_weight_kg,
    avg_rpe,
    avg_sets_per_performance,
    avg_reps_per_set,
    first_performed_date,
    last_performed_date,
    days_since_last_performed,
    popularity_rank,
    muscle_group_rank
from ranked_exercises
order by times_performed desc, total_volume_kg desc
