--- Get service ids by type of weekday
select 
	service_id,
	case when sunday = 1 then 'SUNDAY'
		when saturday = 1 then 'SATURDAY'
		else 'WEEKDAY' end as calendar_type
from calendar
where end_date >= 20230425


-- make route shapes
select 
    st_makeline(array_agg(st_makepoint(shape_pt_lon, shape_pt_lat))),
    shape_id 
from
    shapes
group by
    shape_id


---- get stop times for a specific station
select trip_id
from trips
where service_id = 78
and trip_headsign = 'Philadelphia'


select arrival_time 
from stop_times
where trip_id in (
	select trip_id
	from trips
	where service_id = 78
	and trip_headsign = 'Philadelphia'
)
and stop_id = 4
order by arrival_time 



select arrival_time 
from stop_times
where trip_id in (
	select trip_id
	from trips
	where service_id = 78
	and trip_headsign = 'Lindenwold'
)
and stop_id = 10
order by arrival_time 