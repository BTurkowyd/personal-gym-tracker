-- Test that exercise_frequency has positive counts
-- All count metrics should be greater than 0

select
    exercise_name,
    times_performed,
    total_sets
from {{ ref('exercise_frequency') }}
where times_performed <= 0 
   or total_sets <= 0
