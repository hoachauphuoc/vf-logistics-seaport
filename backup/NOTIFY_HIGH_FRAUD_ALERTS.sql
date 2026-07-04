CREATE OR REPLACE PROCEDURE MENDIX_APP.AGENTS.NOTIFY_HIGH_FRAUD_ALERTS()
RETURNS VARIANT
LANGUAGE SQL
COMMENT = 'Sends email notification when HIGH severity fraud alerts are detected. Uses Snowflake native email integration.'
EXECUTE AS OWNER
AS
DECLARE
    v_high_count INT;
    v_alert_summary VARCHAR;
    v_subject VARCHAR;
    v_body VARCHAR;
BEGIN
    -- Count new HIGH alerts (last 6 hours, not yet notified)
    SELECT COUNT(*) INTO :v_high_count
    FROM MENDIX_APP.AGENTS.FRAUD_ALERT
    WHERE STATUS = 'OPEN' AND SEVERITY = 'HIGH'
    AND CREATED_AT >= DATEADD(HOUR, -6, CURRENT_TIMESTAMP());

    IF (:v_high_count = 0) THEN
        RETURN OBJECT_CONSTRUCT('status', 'NO_ACTION', 'message', 'No new HIGH alerts to notify');
    END IF;

    -- Build summary
    SELECT LISTAGG(ALERT_TYPE || ': ' || LEFT(DESCRIPTION, 80), ' | ') INTO :v_alert_summary
    FROM MENDIX_APP.AGENTS.FRAUD_ALERT
    WHERE STATUS = 'OPEN' AND SEVERITY = 'HIGH'
    AND CREATED_AT >= DATEADD(HOUR, -6, CURRENT_TIMESTAMP());

    v_subject := 'VF Logistics FRAUD ALERT: ' || :v_high_count || ' HIGH severity alert(s) detected';
    v_body := 'VF Logistics Automated Fraud Detection System' ||
              '\n\n' || :v_high_count || ' HIGH severity alert(s) require immediate attention:' ||
              '\n\n' || :v_alert_summary ||
              '\n\nAction Required: Review alerts in VF Logistics Dashboard > Fraud Detection page.' ||
              '\n\nThis is an automated notification from TASK_NOTIFY_HIGH_FRAUD.';

    -- Send email via Snowflake notification
    CALL SYSTEM$SEND_EMAIL(
        'VF_LOGISTICS_EMAIL_NOTIFY',
        'cnttmeovat@gmail.com',
        :v_subject,
        :v_body
    );

    RETURN OBJECT_CONSTRUCT('status', 'SENT', 'high_alerts', :v_high_count, 'subject', :v_subject);
END
