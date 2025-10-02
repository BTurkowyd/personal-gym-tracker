-- Equipment usage trends mart: usage by week and month

{{ config(materialized='view') }}

with exercises as (
    select * from {{ ref('stg_exercises') }}
),
workouts as (
    select * from {{ ref('stg_workouts') }}
),

exercises_with_date as (
    select
        e.*, w.workout_date
    from exercises e
    inner join workouts w on e.workout_id = w.workout_id
),

weekly_usage as (
    select
        equipment_category,
        date_trunc('week', workout_date) as week,
        count(*) as uses
    from exercises_with_date
    where equipment_category is not null
    group by equipment_category, date_trunc('week', workout_date)
),

monthly_usage as (
    select
        equipment_category,
        date_trunc('month', workout_date) as month,
        count(*) as uses
    from exercises_with_date
    where equipment_category is not null
    group by equipment_category, date_trunc('month', workout_date)
)

select 'weekly' as period, equipment_category, week as period_start, uses from weekly_usage
union all
select 'monthly' as period, equipment_category, month as period_start, uses from monthly_usage
order by equipment_category, period_start desc
