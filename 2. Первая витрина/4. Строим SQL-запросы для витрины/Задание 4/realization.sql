-- Поменяйте этот код
SELECT ua.client_id,
       ua.utm_campaign,
       ual.fst_visit_dt,
       ual.registration_dt,
       ual.is_registration,
       upl.total_payment_amount
FROM user_attributes AS ua
LEFT JOIN (
       SELECT client_id,
              DATE(MIN(CASE WHEN action = 'visit' THEN hitdatetime ELSE NULL END)) AS fst_visit_dt,
              DATE(MIN(CASE WHEN action = 'registration' THEN hitdatetime ELSE NULL END)) AS registration_dt,
              MAX(CASE WHEN action = 'registration' THEN 1 ELSE 0 END) AS is_registration
       FROM user_activity_log
       GROUP BY client_id
) AS ual
ON ua.client_id = ual.client_id
LEFT JOIN (
       SELECT client_id,
              SUM(payment_amount) AS total_payment_amount
       FROM user_payment_log
       GROUP BY client_id
) AS upl
ON ua.client_id = upl.client_id;