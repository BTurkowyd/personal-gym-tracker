-- Set/Rep and RPE distribution mart: histograms and percentiles

{{ config(materialized='view') }}

with sets as (
    select * from {{ ref('stg_sets') }}
),

set_distribution as (
    select
        set_order,
        count(*) as set_count
    from sets
    group by set_order
),

rep_distribution as (
    select
        reps,
        count(*) as rep_count
    from sets
    group by reps
),

rpe_distribution as (
    select
        round(rate_of_perceived_exertion, 0) as rpe_rounded,
        count(*) as rpe_count
    from sets
    group by round(rate_of_perceived_exertion, 0)
),

rpe_percentiles as (
    select
        approx_percentile(rate_of_perceived_exertion, 0.5) as median_rpe,
        approx_percentile(rate_of_perceived_exertion, 0.9) as p90_rpe,
        approx_percentile(rate_of_perceived_exertion, 0.95) as p95_rpe
    from sets
)

select 'set_distribution' as metric, 
    cast(set_order as varchar) as col1, 
    cast(set_count as varchar) as col2, 
    null as col3, 
    null as col4
from set_distribution
union all
select 'rep_distribution' as metric, 
    cast(reps as varchar) as col1, 
    cast(rep_count as varchar) as col2, 
    null as col3, 
    null as col4
from rep_distribution
union all
select 'rpe_distribution' as metric, 
    cast(rpe_rounded as varchar) as col1, 
    cast(rpe_count as varchar) as col2, 
    null as col3, 
    null as col4
from rpe_distribution
union all
select 'rpe_percentiles' as metric, 
    null as col1, 
    cast(median_rpe as varchar) as col2, 
    cast(p90_rpe as varchar) as col3, 
    cast(p95_rpe as varchar) as col4
from rpe_percentiles
