-- Personal Records (PR) tracking mart
-- Tracks current PRs for each exercise and provides PR progression history

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

exercise_max_weights as (
    select
        e.exercise_name,
        e.muscle_group,
        e.equipment_category,
        w.workout_date,
        w.workout_id,
        e.exercise_id,
        max(s.weight_kg) as max_weight_kg,
        max(s.reps) as max_reps_at_weight
    from exercises e
    inner join sets s on e.exercise_id = s.exercise_id
    inner join workouts w on e.workout_id = w.workout_id
    where s.weight_kg > 0  -- Only consider sets with weight
    group by
        e.exercise_name,
        e.muscle_group,
        e.equipment_category,
        w.workout_date,
        w.workout_id,
        e.exercise_id
),

current_prs as (
    select
        exercise_name,
        muscle_group,
        equipment_category,
        max(max_weight_kg) as current_pr_weight,
        max(workout_date) as pr_date
    from exercise_max_weights
    group by
        exercise_name,
        muscle_group,
        equipment_category
),

pr_history as (
    select
        emw.exercise_name,
        emw.muscle_group,
        emw.equipment_category,
        emw.workout_date,
        emw.max_weight_kg,
        emw.max_reps_at_weight,
        -- Calculate if this was a PR at the time
        max(emw.max_weight_kg) over (
            partition by emw.exercise_name 
            order by emw.workout_date 
            rows between unbounded preceding and current row
        ) as pr_at_date,
        -- Calculate previous PR weight
        lag(max(emw.max_weight_kg) over (
            partition by emw.exercise_name 
            order by emw.workout_date 
            rows between unbounded preceding and current row
        ), 1) over (
            partition by emw.exercise_name 
            order by emw.workout_date
        ) as previous_pr_weight,
        -- Flag if this workout set a new PR
        case
            when emw.max_weight_kg = max(emw.max_weight_kg) over (
                partition by emw.exercise_name 
                order by emw.workout_date 
                rows between unbounded preceding and current row
            )
            and emw.max_weight_kg > coalesce(
                lag(max(emw.max_weight_kg) over (
                    partition by emw.exercise_name 
                    order by emw.workout_date 
                    rows between unbounded preceding and current row
                ), 1) over (
                    partition by emw.exercise_name 
                    order by emw.workout_date
                ), 0)
            then true
            else false
        end as is_new_pr
    from exercise_max_weights emw
)

select
    cp.exercise_name,
    cp.muscle_group,
    cp.equipment_category,
    cp.current_pr_weight,
    cp.pr_date as current_pr_date,
    date_diff('day', cp.pr_date, current_date) as days_since_pr,
    -- Get first PR details
    (
        select min(workout_date) 
        from pr_history ph2 
        where ph2.exercise_name = cp.exercise_name 
        and ph2.is_new_pr = true
    ) as first_pr_date,
    (
        select min(max_weight_kg) 
        from pr_history ph2 
        where ph2.exercise_name = cp.exercise_name
    ) as starting_weight,
    -- Calculate total improvement
    round(
        cp.current_pr_weight - coalesce((
            select min(max_weight_kg) 
            from pr_history ph2 
            where ph2.exercise_name = cp.exercise_name
        ), 0),
        2
    ) as total_weight_improvement,
    -- Calculate improvement percentage
    round(
        case
            when (select min(max_weight_kg) from pr_history ph2 where ph2.exercise_name = cp.exercise_name) > 0
            then (
                (cp.current_pr_weight - (select min(max_weight_kg) from pr_history ph2 where ph2.exercise_name = cp.exercise_name)) 
                / (select min(max_weight_kg) from pr_history ph2 where ph2.exercise_name = cp.exercise_name)
            ) * 100
            else 0
        end,
        2
    ) as improvement_percentage,
    -- Count how many times PR was broken
    (
        select count(*) 
        from pr_history ph2 
        where ph2.exercise_name = cp.exercise_name 
        and ph2.is_new_pr = true
    ) as pr_count
from current_prs cp
order by cp.current_pr_weight desc, cp.exercise_name
