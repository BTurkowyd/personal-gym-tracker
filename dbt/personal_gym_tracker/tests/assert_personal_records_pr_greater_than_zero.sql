-- Test that all PRs in personal_records have weight greater than 0
-- PRs should always be positive weights

select
    exercise_name,
    current_pr_weight
from {{ ref('personal_records') }}
where current_pr_weight <= 0
