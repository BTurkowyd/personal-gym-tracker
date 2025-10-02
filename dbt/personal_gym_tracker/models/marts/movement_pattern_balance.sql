-- Movement pattern balance mart: push/pull/legs/core balance
-- NOTE: This requires a mapping of exercises to movement patterns. If not available, this mart will be a placeholder.

{{ config(materialized='view') }}

with exercises as (
    select *,
        -- Example mapping, replace with your actual mapping logic or table
        case
            when lower(exercise_name) like '%bench%' or lower(exercise_name) like '%press%' then 'push'
            when lower(exercise_name) like '%row%' or lower(exercise_name) like '%pull%' or lower(exercise_name) like '%curl%' then 'pull'
            when lower(exercise_name) like '%squat%' or lower(exercise_name) like '%deadlift%' or lower(exercise_name) like '%leg%' then 'legs'
            when lower(exercise_name) like '%plank%' or lower(exercise_name) like '%crunch%' or lower(exercise_name) like '%core%' then 'core'
            else 'other'
        end as movement_pattern
    from {{ ref('stg_exercises') }}
),

pattern_counts as (
    select
        movement_pattern,
        count(*) as exercise_count
    from exercises
    group by movement_pattern
)

select * from pattern_counts
order by exercise_count desc
