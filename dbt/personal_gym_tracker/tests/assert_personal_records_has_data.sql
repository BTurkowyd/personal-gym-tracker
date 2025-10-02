-- Test that personal_records mart has at least one row
-- This ensures the mart is being built correctly

select
    count(*) as record_count
from {{ ref('personal_records') }}
having count(*) = 0
