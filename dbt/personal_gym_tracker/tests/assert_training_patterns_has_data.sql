-- Test that training_patterns mart has at least one row
-- This ensures the mart is being built correctly

select
    count(*) as record_count
from {{ ref('training_patterns') }}
having count(*) = 0
