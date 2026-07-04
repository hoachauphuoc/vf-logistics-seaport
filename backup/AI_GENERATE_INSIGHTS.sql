CREATE OR REPLACE PROCEDURE MENDIX_APP.AGENTS.AI_GENERATE_INSIGHTS(P_LANGUAGE VARCHAR DEFAULT 'EN')
RETURNS VARIANT
LANGUAGE SQL
COMMENT = 'Proactive AI Insights: Analyzes shipment records to discover trends, patterns, risks. Generates executive-level insights without human prompting.'
EXECUTE AS OWNER
AS
DECLARE
    v_total INT;
    v_pending INT;
    v_in_transit INT;
    v_sap_posted INT;
    v_open_alerts INT;
    v_high_alerts INT;
    v_avg_charge FLOAT;
    v_total_revenue FLOAT;
    v_top_carrier VARCHAR;
    v_ai_cost FLOAT;
    v_stats VARCHAR;
    v_prompt VARCHAR;
    v_ai_result VARIANT;
    v_lang VARCHAR;
BEGIN
    IF (:P_LANGUAGE = 'VN') THEN
        v_lang := 'Respond in Vietnamese.';
    ELSEIF (:P_LANGUAGE = 'JA') THEN
        v_lang := 'Respond in Japanese.';
    ELSE
        v_lang := 'Respond in English.';
    END IF;

    SELECT COUNT(*) INTO :v_total FROM MENDIX_APP.AGENTS.BILL_OF_LADING;
    SELECT COUNT(*) INTO :v_pending FROM MENDIX_APP.AGENTS.BILL_OF_LADING WHERE STATUS IN ('Pending_Review','PENDING','DRAFT');
    SELECT COUNT(*) INTO :v_in_transit FROM MENDIX_APP.AGENTS.BILL_OF_LADING WHERE STATUS = 'In_Transit';
    SELECT COUNT(*) INTO :v_sap_posted FROM MENDIX_APP.AGENTS.BILL_OF_LADING WHERE STATUS = 'SAP_POSTED';
    SELECT COUNT(*) INTO :v_open_alerts FROM MENDIX_APP.AGENTS.FRAUD_ALERT WHERE STATUS = 'OPEN';
    SELECT COUNT(*) INTO :v_high_alerts FROM MENDIX_APP.AGENTS.FRAUD_ALERT WHERE STATUS = 'OPEN' AND SEVERITY = 'HIGH';
    SELECT ROUND(AVG(TOTAL_CHARGES), 2) INTO :v_avg_charge FROM MENDIX_APP.AGENTS.BILL_OF_LADING;
    SELECT ROUND(SUM(TOTAL_CHARGES), 0) INTO :v_total_revenue FROM MENDIX_APP.AGENTS.BILL_OF_LADING;
    SELECT CARRIER_NAME INTO :v_top_carrier FROM MENDIX_APP.AGENTS.BILL_OF_LADING GROUP BY CARRIER_NAME ORDER BY COUNT(*) DESC LIMIT 1;
    SELECT COALESCE(ROUND(SUM(TOTAL_TOKENS)*0.000001, 4), 0) INTO :v_ai_cost FROM MENDIX_APP.AGENTS.AI_CALL_LOG WHERE CALL_TIMESTAMP >= CURRENT_DATE();

    v_stats := 'Total shipments: ' || :v_total || ', Pending: ' || :v_pending || ', In Transit: ' || :v_in_transit || ', SAP Posted: ' || :v_sap_posted || ', Open fraud alerts: ' || :v_open_alerts || ' (HIGH: ' || :v_high_alerts || '), Avg charge: $' || :v_avg_charge || ', Total revenue: $' || :v_total_revenue || ', Top carrier: ' || :v_top_carrier || ', AI cost today: $' || :v_ai_cost;

    v_prompt := 'You are a senior maritime logistics analyst. ' || :v_lang || ' Analyze this operational data and generate exactly 5 executive insights. Focus on: risks, opportunities, anomalies, trends, and actionable recommendations. Data: ' || :v_stats || '. Return JSON array only, no other text: [{"category":"RISK","title":"<short>","insight":"<2-3 sentences>","priority":"HIGH"},{"category":"OPPORTUNITY","title":"<short>","insight":"<2-3 sentences>","priority":"MEDIUM"},{"category":"TREND","title":"<short>","insight":"<2-3 sentences>","priority":"LOW"},{"category":"ANOMALY","title":"<short>","insight":"<2-3 sentences>","priority":"HIGH"},{"category":"RECOMMENDATION","title":"<short>","insight":"<2-3 sentences>","priority":"MEDIUM"}]';

    CALL MENDIX_APP.AGENTS.AI_COMPLETE_WITH_RETRY('llama3-8b', :v_prompt, 2, 'AI_GENERATE_INSIGHTS') INTO :v_ai_result;

    IF (:v_ai_result:status::VARCHAR = 'SUCCESS') THEN
        INSERT INTO MENDIX_APP.AGENTS.AI_ANOMALY_REPORT
            (ANOMALY_TYPE, SEVERITY, BL_IDS, BUSINESS_EXPLANATION, RECOMMENDED_ACTIONS, LANGUAGE, GENERATED_BY)
        VALUES ('PROACTIVE_INSIGHT', 'INFO', 'SYSTEM', :v_ai_result:response::VARCHAR, 'Review in dashboard', :P_LANGUAGE, 'AI_INSIGHTS');

        RETURN OBJECT_CONSTRUCT('status', 'SUCCESS', 'insights', :v_ai_result:response::VARCHAR, 'data_summary', :v_stats, 'language', :P_LANGUAGE);
    ELSE
        RETURN OBJECT_CONSTRUCT('status', 'FAILED', 'error', :v_ai_result:error::VARCHAR);
    END IF;
END
