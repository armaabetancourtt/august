select
 cast(event_id as {{ dbt.type_string() }}) as event_id,
 cast(property_id as {{ dbt.type_string() }}) as property_id,
 cast(occurred_at as timestamp) as occurred_at,
 cast(amount as {{ dbt.type_numeric() }}) as amount,
 lower(trim(event_type)) as event_type
from {{ source('august_raw','property_events') }}
where event_id is not null and property_id is not null and occurred_at is not null
  and amount >= 0 and lower(trim(event_type)) in ('listing','sale','rental')
