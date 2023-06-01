-- Поменяйте этот код
SELECT client_id,
       DATE(MIN(CASE WHEN action = 'visit' THEN hitdatetime ELSE NULL END)) AS fst_visit_dt,
       DATE(MIN(CASE WHEN action = 'registration' THEN hitdatetime ELSE NULL END)) AS registration_dt,
       MAX(CASE WHEN action = 'registration' THEN 1 ELSE 0 END) AS is_registration
FROM user_activity_log
GROUP BY client_id
LIMIT 10;