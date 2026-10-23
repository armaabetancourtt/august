select property_id,min(occurred_at) as first_seen_at,max(occurred_at) as last_seen_at,
count(*) as observed_events
from {{ ref('stg_property_events') }}
group by property_id
