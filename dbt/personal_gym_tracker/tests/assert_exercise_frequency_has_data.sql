-- Test that exercise_frequency mart has at least one row
-- This ensures the mart is being built correctly

select
    count(*) as record_count
from {{ ref('exercise_frequency') }}
having count(*) = 0
