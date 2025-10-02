-- Streaks mart: tracks current and longest streaks of consecutive training days

{{ config(materialized='view') }}

with workout_dates as (
    select distinct workout_date
    from {{ ref('stg_workouts') }}
    order by workout_date
),

streaks as (
    select
        workout_date,
        row_number() over (order by workout_date) as rn,
        workout_date - interval '1' day * (row_number() over (order by workout_date)) as streak_group
    from workout_dates
),

streak_groups as (
    select
        min(workout_date) as streak_start,
        max(workout_date) as streak_end,
        count(*) as streak_length
    from streaks
    group by streak_group
)

select
    streak_start,
    streak_end,
    streak_length
from streak_groups
order by streak_length desc, streak_end desc
