-- Exercise performance tracking
-- Shows progression and statistics for each exercise over time

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

exercise_sets as (
    select
        e.exercise_name,
        e.muscle_group,
        e.equipment_category,
        w.workout_date,
        w.workout_id,
        e.exercise_id,
        s.set_order,
        s.reps,
        s.weight_kg,
        s.set_volume_kg,
        s.rate_of_perceived_exertion
    from exercises e
    inner join sets s on e.exercise_id = s.exercise_id
    inner join workouts w on e.workout_id = w.workout_id
),

exercise_stats as (
    select
        exercise_name,
        muscle_group,
        equipment_category,
        workout_date,
        workout_id,
        exercise_id,
        count(*) as total_sets,
        round(sum(set_volume_kg), 2) as total_volume_kg,
        round(max(weight_kg), 2) as max_weight_kg,
        sum(reps) as total_reps,
        round(avg(rate_of_perceived_exertion), 2) as avg_rpe
    from exercise_sets
    group by
        exercise_name,
        muscle_group,
        equipment_category,
        workout_date,
        workout_id,
        exercise_id
),

personal_bests as (
    select
        *,
        -- Calculate personal best for this exercise up to this date
        round(max(max_weight_kg) over (
            partition by exercise_name 
            order by workout_date 
            rows between unbounded preceding and current row
        ), 2) as personal_best_weight
    from exercise_stats
)

select
    *,
    -- Flag if this is a new personal best
    case
        when max_weight_kg = personal_best_weight then true
        else false
    end as is_personal_best
from personal_bests
order by workout_date desc, exercise_name
