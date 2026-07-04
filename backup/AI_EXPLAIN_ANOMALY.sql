CREATE OR REPLACE PROCEDURE MENDIX_APP.AGENTS.AI_EXPLAIN_ANOMALY(P_LANGUAGE VARCHAR DEFAULT 'EN')
RETURNS VARIANT
LANGUAGE SQL
COMMENT = 'Proactive AI: Scans OPEN fraud alerts, generates business-language explanations and recommended actions. Zero human trigger needed.'
EXECUTE AS OWNER
AS
DECLARE
    v_prompt VARCHAR;
    v_ai_result VARIANT;
    v_explanation VARCHAR;
    v_actions VARCHAR;
    v_reports_created INT DEFAULT 0;
    v_lang VARCHAR;
    v_type VARCHAR;
    v_sev VARCHAR;
    v_desc VARCHAR;
    v_docs VARCHAR;
    c1 CURSOR FOR
        SELECT ALERT_TYPE, SEVERITY, LEFT(DESCRIPTION, 200) as DESC_SHORT, DOCUMENT_IDS
        FROM MENDIX_APP.AGENTS.FRAUD_ALERT
        WHERE STATUS = 'OPEN'
        ORDER BY CREATED_AT DESC
        LIMIT 5;
BEGIN
    IF (:P_LANGUAGE = 'VN') THEN
        v_lang := 'Respond in Vietnamese.';
    ELSEIF (:P_LANGUAGE = 'JA') THEN
        v_lang := 'Respond in Japanese.';
    ELSE
        v_lang := 'Respond in English.';
    END IF;

    OPEN c1;
    FOR rec IN c1 DO
        v_type := rec.ALERT_TYPE;
        v_sev := rec.SEVERITY;
        v_desc := rec.DESC_SHORT;
        v_docs := rec.DOCUMENT_IDS;

        v_prompt := 'You are a senior maritime logistics compliance officer. ' || :v_lang || ' Explain this anomaly for business stakeholders (non-technical): Type=' || :v_type || ', Severity=' || :v_sev || ', Details=' || COALESCE(:v_desc, 'Unknown') || '. Return JSON: {"explanation":"<2-3 sentences: what happened, why it matters, financial risk>","actions":"<3 recommended actions comma-separated>"}';

        CALL MENDIX_APP.AGENTS.AI_COMPLETE_WITH_RETRY('llama3-8b', :v_prompt, 2, 'AI_EXPLAIN_ANOMALY') INTO :v_ai_result;

        IF (:v_ai_result:status::VARCHAR = 'SUCCESS') THEN
            v_explanation := COALESCE(TRY_PARSE_JSON(:v_ai_result:response::VARCHAR):explanation::VARCHAR, :v_ai_result:response::VARCHAR);
            v_actions := COALESCE(TRY_PARSE_JSON(:v_ai_result:response::VARCHAR):actions::VARCHAR, 'Review alert, Escalate to compliance, Document findings');

            INSERT INTO MENDIX_APP.AGENTS.AI_ANOMALY_REPORT
                (ANOMALY_TYPE, SEVERITY, BL_IDS, BUSINESS_EXPLANATION, RECOMMENDED_ACTIONS, LANGUAGE)
            VALUES (:v_type, :v_sev, :v_docs, :v_explanation, :v_actions, :P_LANGUAGE);

            v_reports_created := :v_reports_created + 1;
        END IF;
    END FOR;
    CLOSE c1;

    RETURN OBJECT_CONSTRUCT('status', 'SUCCESS', 'reports_generated', :v_reports_created, 'language', :P_LANGUAGE);
END
