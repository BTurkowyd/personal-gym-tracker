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

-- Get max weight per exercise per workout
exercise_max_weights as (
    select
        e.exercise_name,
        e.muscle_group,
        e.equipment_category,
        w.workout_date,
        max(s.weight_kg) as max_weight_kg
    from exercises e
    inner join sets s on e.exercise_id = s.exercise_id
    inner join workouts w on e.workout_id = w.workout_id
    where s.weight_kg > 0  -- Only consider sets with weight
    group by
        e.exercise_name,
        e.muscle_group,
        e.equipment_category,
        w.workout_date
),

-- Calculate running max (PR at each date)
pr_progression as (
    select
        exercise_name,
        muscle_group,
        equipment_category,
        workout_date,
        max_weight_kg,
        max(max_weight_kg) over (
            partition by exercise_name 
            order by workout_date 
            rows between unbounded preceding and current row
        ) as running_pr
    from exercise_max_weights
),

-- Flag when new PRs are set
pr_milestones as (
    select
        *,
        case 
            when max_weight_kg = running_pr 
            and (lag(running_pr) over (partition by exercise_name order by workout_date) is null
                 or max_weight_kg > lag(running_pr) over (partition by exercise_name order by workout_date))
            then true 
            else false 
        end as is_new_pr
    from pr_progression
),

-- Get current PR for each exercise
current_prs as (
    select
        exercise_name,
        muscle_group,
        equipment_category,
        max(running_pr) as current_pr_weight
    from pr_milestones
    group by exercise_name, muscle_group, equipment_category
),

-- Get the date when current PR was achieved
pr_dates as (
    select
        pm.exercise_name,
        max(pm.workout_date) as current_pr_date
    from pr_milestones pm
    inner join current_prs cp 
        on pm.exercise_name = cp.exercise_name 
        and pm.max_weight_kg = cp.current_pr_weight
    group by pm.exercise_name
),

-- Get starting weights and first PR dates
starting_stats as (
    select
        exercise_name,
        min(max_weight_kg) as starting_weight,
        min(workout_date) as first_workout_date,
        min(case when is_new_pr then workout_date end) as first_pr_date
    from pr_milestones
    group by exercise_name
),

-- Count PR achievements
pr_counts as (
    select
        exercise_name,
        sum(case when is_new_pr then 1 else 0 end) as pr_count
    from pr_milestones
    group by exercise_name
)

select
    cp.exercise_name,
    cp.muscle_group,
    cp.equipment_category,
    cp.current_pr_weight,
    pd.current_pr_date,
    date_diff('day', pd.current_pr_date, current_date) as days_since_pr,
    ss.first_pr_date,
    ss.starting_weight,
    round(cp.current_pr_weight - coalesce(ss.starting_weight, 0), 2) as total_weight_improvement,
    round(
        case
            when ss.starting_weight > 0
            then ((cp.current_pr_weight - ss.starting_weight) / ss.starting_weight) * 100
            else 0
        end,
        2
    ) as improvement_percentage,
    pc.pr_count
from current_prs cp
left join pr_dates pd on cp.exercise_name = pd.exercise_name
left join starting_stats ss on cp.exercise_name = ss.exercise_name
left join pr_counts pc on cp.exercise_name = pc.exercise_name
order by cp.current_pr_weight desc, cp.exercise_name
