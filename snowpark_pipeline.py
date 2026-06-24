# VF Logistics - Snowpark Python Data Pipeline
# This pipeline demonstrates Snowpark-based data transformation for the seaport platform

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, when, lit, count, avg, sum as sum_, max as max_, min as min_
from snowflake.snowpark.functions import current_timestamp, datediff, to_date
from snowflake.snowpark.types import StringType, IntegerType, FloatType
import json

def create_session():
    """Create Snowpark session using key-pair auth"""
    connection_params = {
        "account": "JMAXFXA-XN12202",
        "user": "CNNTMEOVAT",
        "database": "MENDIX_APP",
        "schema": "AGENTS",
        "warehouse": "COMPUTE_WH",
        "role": "ACCOUNTADMIN",
        "private_key_file": "path/to/snowflake_key.p8"  # Update path
    }
    return Session.builder.configs(connection_params).create()


def pipeline_shipment_analytics(session: Session):
    """
    Transform raw B/L data into analytics-ready aggregations.
    Demonstrates: DataFrame operations, joins, window functions, aggregations.
    """
    # Read source data
    bl_df = session.table("BILL_OF_LADING")
    ports_df = session.table("PORT_MASTER")
    hs_df = session.table("HS_CODE_REFERENCE")
    
    # 1. Enrich B/L with port details
    enriched = (
        bl_df
        .join(
            ports_df.select(
                col("PORT_CODE").alias("POL_CODE"),
                col("PORT_NAME").alias("POL_NAME"),
                col("COUNTRY").alias("POL_COUNTRY"),
                col("TIMEZONE").alias("POL_TIMEZONE")
            ),
            bl_df["PORT_OF_LOADING_LOCODE"] == col("POL_CODE"),
            "left"
        )
        .join(
            ports_df.select(
                col("PORT_CODE").alias("POD_CODE"),
                col("PORT_NAME").alias("POD_NAME"),
                col("COUNTRY").alias("POD_COUNTRY"),
                col("TIMEZONE").alias("POD_TIMEZONE")
            ),
            bl_df["PORT_OF_DISCHARGE_LOCODE"] == col("POD_CODE"),
            "left"
        )
    )
    
    # 2. Classify shipments by weight category
    classified = enriched.with_column(
        "WEIGHT_CATEGORY",
        when(col("GROSS_WEIGHT_KGS") > 20000, lit("Heavy Cargo"))
        .when(col("GROSS_WEIGHT_KGS") > 10000, lit("Medium Cargo"))
        .otherwise(lit("Light Cargo"))
    ).with_column(
        "CONTAINER_SIZE",
        when(col("CONTAINER_TYPE").contains("40"), lit("40ft"))
        .when(col("CONTAINER_TYPE").contains("20"), lit("20ft"))
        .otherwise(lit("Other"))
    )
    
    # 3. Route analytics
    route_stats = (
        classified
        .group_by("POL_COUNTRY", "POD_COUNTRY")
        .agg(
            count("*").alias("SHIPMENT_COUNT"),
            avg("GROSS_WEIGHT_KGS").alias("AVG_WEIGHT_KG"),
            sum_("TOTAL_CHARGES").alias("TOTAL_REVENUE"),
            avg("TOTAL_CHARGES").alias("AVG_CHARGES")
        )
        .sort(col("SHIPMENT_COUNT").desc())
    )
    
    # 4. Carrier performance
    carrier_stats = (
        classified
        .group_by("CARRIER_NAME")
        .agg(
            count("*").alias("TOTAL_SHIPMENTS"),
            avg("GROSS_WEIGHT_KGS").alias("AVG_WEIGHT"),
            sum_("TOTAL_CHARGES").alias("TOTAL_REVENUE"),
            count(when(col("STATUS") == "In_Transit", True)).alias("IN_TRANSIT"),
            count(when(col("STATUS") == "Approved", True)).alias("APPROVED")
        )
    )
    
    # 5. Write results to analytics tables
    route_stats.write.mode("overwrite").save_as_table("ANALYTICS_ROUTE_SUMMARY")
    carrier_stats.write.mode("overwrite").save_as_table("ANALYTICS_CARRIER_PERFORMANCE")
    
    return {
        "routes_processed": route_stats.count(),
        "carriers_processed": carrier_stats.count()
    }


def pipeline_ai_usage_report(session: Session):
    """
    Process AI call logs into daily/weekly usage reports.
    Demonstrates: Date aggregation, cost calculation, error rate analysis.
    """
    ai_logs = session.table("AI_CALL_LOG")
    
    # Daily summary with cost estimation
    daily_report = (
        ai_logs
        .with_column("CALL_DATE", to_date(col("CALL_TIMESTAMP")))
        .group_by("CALL_DATE", "MODEL_NAME", "PROCEDURE_NAME")
        .agg(
            count("*").alias("TOTAL_CALLS"),
            sum_("INPUT_TOKENS").alias("TOTAL_INPUT_TOKENS"),
            sum_("OUTPUT_TOKENS").alias("TOTAL_OUTPUT_TOKENS"),
            sum_("TOTAL_TOKENS").alias("TOTAL_TOKENS"),
            avg("LATENCY_MS").alias("AVG_LATENCY_MS"),
            max_("LATENCY_MS").alias("MAX_LATENCY_MS"),
            count(when(col("STATUS").contains("ERROR"), True)).alias("ERROR_COUNT")
        )
        .with_column(
            "EST_COST_USD",
            (col("TOTAL_INPUT_TOKENS") / 1000000.0 * 0.05) + 
            (col("TOTAL_OUTPUT_TOKENS") / 1000000.0 * 0.10)
        )
        .with_column(
            "ERROR_RATE_PCT",
            (col("ERROR_COUNT") * 100.0 / col("TOTAL_CALLS"))
        )
        .sort(col("CALL_DATE").desc())
    )
    
    daily_report.write.mode("overwrite").save_as_table("ANALYTICS_AI_DAILY_REPORT")
    
    return {"days_processed": daily_report.count()}


def pipeline_compliance_dashboard(session: Session):
    """
    Build compliance readiness dashboard data.
    Demonstrates: Multi-table joins, conditional logic, compliance scoring.
    """
    bl_df = session.table("BILL_OF_LADING")
    compliance_df = session.table("COMPLIANCE_CHECK_RESULT")
    hs_df = session.table("HS_CODE_REFERENCE")
    
    # Compliance score per shipment
    compliance_scores = (
        compliance_df
        .group_by("DOCUMENT_ID")
        .agg(
            count("*").alias("TOTAL_CHECKS"),
            count(when(col("CHECK_STATUS") == "PASS", True)).alias("PASSED"),
            count(when(col("CHECK_STATUS") == "FAIL", True)).alias("FAILED"),
            count(when(col("CHECK_STATUS") == "WARNING", True)).alias("WARNINGS")
        )
        .with_column(
            "COMPLIANCE_SCORE",
            (col("PASSED") * 100.0 / col("TOTAL_CHECKS"))
        )
        .with_column(
            "RISK_LEVEL",
            when(col("FAILED") > 0, lit("HIGH"))
            .when(col("WARNINGS") > 0, lit("MEDIUM"))
            .otherwise(lit("LOW"))
        )
    )
    
    # Join with B/L for full picture
    dashboard_data = (
        bl_df
        .select("BL_ID", "BL_NUMBER", "VESSEL_NAME", "CARRIER_NAME",
                "PORT_OF_LOADING_LOCODE", "PORT_OF_DISCHARGE_LOCODE", "STATUS")
        .join(compliance_scores, bl_df["BL_ID"] == compliance_scores["DOCUMENT_ID"], "left")
    )
    
    dashboard_data.write.mode("overwrite").save_as_table("ANALYTICS_COMPLIANCE_DASHBOARD")
    
    return {"shipments_scored": dashboard_data.count()}


def run_full_pipeline(session: Session):
    """Execute all pipeline stages"""
    print("=" * 60)
    print("VF LOGISTICS - SNOWPARK DATA PIPELINE")
    print("=" * 60)
    
    print("\n[1/3] Running Shipment Analytics pipeline...")
    result1 = pipeline_shipment_analytics(session)
    print(f"      Routes: {result1['routes_processed']}, Carriers: {result1['carriers_processed']}")
    
    print("\n[2/3] Running AI Usage Report pipeline...")
    result2 = pipeline_ai_usage_report(session)
    print(f"      Days processed: {result2['days_processed']}")
    
    print("\n[3/3] Running Compliance Dashboard pipeline...")
    result3 = pipeline_compliance_dashboard(session)
    print(f"      Shipments scored: {result3['shipments_scored']}")
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE - Analytics tables refreshed")
    print("=" * 60)
    
    return {"status": "success", "pipelines_run": 3}


# Entry point
if __name__ == "__main__":
    session = create_session()
    run_full_pipeline(session)
    session.close()
