-- Monthly progression mart: best lifts and volume by month

{{ config(materialized='view') }}

with sets as (
    select * from {{ ref('stg_sets') }}
),
workouts as (
    select * from {{ ref('stg_workouts') }}
),

sets_with_date as (
    select
        s.*, w.workout_date
    from sets s
    inner join workouts w on s.workout_id = w.workout_id
),

monthly_lifts as (
    select
        date_trunc('month', workout_date) as month,
        max(weight_kg) as best_lift_kg,
        sum(set_volume_kg) as total_volume_kg
    from sets_with_date
    group by date_trunc('month', workout_date)
)

select
    month,
    best_lift_kg,
    total_volume_kg
from monthly_lifts
order by month desc
