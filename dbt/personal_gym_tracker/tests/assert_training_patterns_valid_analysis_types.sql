-- Test that training_patterns only contains valid analysis types
-- Should only have the 4 defined analysis types

select
    analysis_type
from {{ ref('training_patterns') }}
where analysis_type not in (
    'day_of_week_analysis',
    'time_of_day_analysis', 
    'monthly_analysis',
    'overall_summary'
)
