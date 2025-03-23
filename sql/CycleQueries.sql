```sql
# Total number of rides
SELECT COUNT(ride_id) AS total_rides
FROM `cyclistic-453614.Cyclistic2019.2019Q1`


# Average Trip Duration
SELECT AVG(tripduration_s) AS avg_tripduration
FROM `cyclistic-453614.Cyclistic2019.2019Q1`


# Ratio of casual to members
SELECT usertype, COUNT(*) AS count
FROM `cyclistic-453614.Cyclistic2019.2019Q1`
GROUP BY usertype;



# Peak Usage Hours for Casual Riders
SELECT EXTRACT(HOUR FROM start_time) AS hour, COUNT(*) AS ride_count
FROM `cyclistic-453614.Cyclistic2019.2019Q1`
WHERE usertype = 'casual'
GROUP BY hour
ORDER BY ride_count DESC
LIMIT 5;




# Most Frequent Start Stations for Casual Riders
SELECT start_station_name, COUNT(*) AS ride_count
FROM `cyclistic-453614.Cyclistic2019.2019Q1`
WHERE usertype = 'casual'
GROUP BY start_station_name
ORDER BY ride_count DESC
LIMIT 5;
