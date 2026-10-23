select property_id,date_trunc('month',occurred_at) as event_month,event_type,
count(*) event_count,sum(amount) total_amount,avg(amount) average_amount
from {{ ref('stg_property_events') }}
group by 1,2,3
