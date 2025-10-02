-- Training patterns and consistency analysis
-- Shows day-of-week patterns, consistency metrics, and temporal training patterns

{{ config(
    materialized='view'
) }}

with workouts as (
    select * from {{ ref('stg_workouts') }}
),

sets as (
    select * from {{ ref('stg_sets') }}
),

-- Day of week analysis
day_of_week_stats as (
    select
        day_of_week(w.workout_date) as day_of_week_num,
        case day_of_week(w.workout_date)
            when 1 then 'Monday'
            when 2 then 'Tuesday'
            when 3 then 'Wednesday'
            when 4 then 'Thursday'
            when 5 then 'Friday'
            when 6 then 'Saturday'
            when 7 then 'Sunday'
        end as day_name,
        count(distinct w.workout_id) as workout_count,
        round(avg(w.workout_duration_minutes), 2) as avg_duration_minutes,
        round(sum(w.estimated_volume_kg), 2) as total_volume_kg,
        round(avg(w.estimated_volume_kg), 2) as avg_volume_kg
    from workouts w
    group by day_of_week(w.workout_date)
),

-- Time of day analysis (workout start time)
time_of_day_stats as (
    select
        hour(w.workout_start_datetime) as hour_of_day,
        count(distinct w.workout_id) as workout_count,
        round(avg(w.workout_duration_minutes), 2) as avg_duration_minutes
    from workouts w
    group by hour(w.workout_start_datetime)
),

-- Monthly training patterns
monthly_stats as (
    select
        year(w.workout_date) as year,
        month(w.workout_date) as month,
        date_trunc('month', w.workout_date) as month_start_date,
        count(distinct w.workout_id) as workout_count,
        count(distinct w.workout_date) as training_days,
        round(sum(w.workout_duration_minutes), 2) as total_duration_minutes,
        round(avg(w.workout_duration_minutes), 2) as avg_duration_minutes,
        round(sum(w.estimated_volume_kg), 2) as total_volume_kg,
        round(avg(w.estimated_volume_kg), 2) as avg_volume_per_workout
    from workouts w
    group by year(w.workout_date), month(w.workout_date), date_trunc('month', w.workout_date)
),

-- Rest days and consistency
workout_dates as (
    select distinct
        workout_date,
        lag(workout_date) over (order by workout_date) as previous_workout_date
    from workouts
),

rest_day_stats as (
    select
        workout_date,
        previous_workout_date,
        date_diff('day', previous_workout_date, workout_date) as days_since_last_workout
    from workout_dates
    where previous_workout_date is not null
),

-- Aggregate all patterns
summary_stats as (
    select
        count(distinct w.workout_id) as total_workouts,
        count(distinct w.workout_date) as total_training_days,
        min(w.workout_date) as first_workout_date,
        max(w.workout_date) as last_workout_date,
        date_diff('day', min(w.workout_date), max(w.workout_date)) as total_days_span,
        -- Calculate consistency metrics
        round(
            cast(count(distinct w.workout_date) as double) / 
            nullif(date_diff('day', min(w.workout_date), max(w.workout_date)), 0) * 100,
            2
        ) as consistency_percentage,
        round(avg(w.workout_duration_minutes), 2) as overall_avg_duration,
        round(sum(w.estimated_volume_kg), 2) as total_volume_all_time,
        -- Rest day statistics
        (select round(avg(days_since_last_workout), 2) from rest_day_stats) as avg_rest_days,
        (select max(days_since_last_workout) from rest_day_stats) as max_rest_days,
        (select min(days_since_last_workout) from rest_day_stats) as min_rest_days
    from workouts w
)

-- Return comprehensive training patterns
select
    'day_of_week_analysis' as analysis_type,
    cast(dow.day_of_week_num as varchar) as dimension,
    dow.day_name as dimension_label,
    dow.workout_count as metric_count,
    dow.avg_duration_minutes as metric_avg_duration,
    dow.total_volume_kg as metric_total_volume,
    dow.avg_volume_kg as metric_avg_volume,
    null as metric_training_days,
    null as metric_consistency_pct
from day_of_week_stats dow

union all

select
    'time_of_day_analysis' as analysis_type,
    cast(tod.hour_of_day as varchar) as dimension,
    cast(tod.hour_of_day as varchar) || ':00' as dimension_label,
    tod.workout_count as metric_count,
    tod.avg_duration_minutes as metric_avg_duration,
    null as metric_total_volume,
    null as metric_avg_volume,
    null as metric_training_days,
    null as metric_consistency_pct
from time_of_day_stats tod

union all

select
    'monthly_analysis' as analysis_type,
    cast(ms.year as varchar) || '-' || lpad(cast(ms.month as varchar), 2, '0') as dimension,
    cast(ms.year as varchar) || '-' || lpad(cast(ms.month as varchar), 2, '0') as dimension_label,
    ms.workout_count as metric_count,
    ms.avg_duration_minutes as metric_avg_duration,
    ms.total_volume_kg as metric_total_volume,
    ms.avg_volume_per_workout as metric_avg_volume,
    ms.training_days as metric_training_days,
    null as metric_consistency_pct
from monthly_stats ms

union all

select
    'overall_summary' as analysis_type,
    'total' as dimension,
    'Overall Training Summary' as dimension_label,
    ss.total_workouts as metric_count,
    ss.overall_avg_duration as metric_avg_duration,
    ss.total_volume_all_time as metric_total_volume,
    null as metric_avg_volume,
    ss.total_training_days as metric_training_days,
    ss.consistency_percentage as metric_consistency_pct
from summary_stats ss

order by analysis_type, dimension
