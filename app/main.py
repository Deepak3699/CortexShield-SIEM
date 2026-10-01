"""
LogSentinel - Main Application
==============================
AI-Powered Intelligent Web Log Analyzer
"""

import logging
import json
import csv
import io
from typing import Dict
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse

# Import modules
from app.ingestion.file_reader import FileReader
from app.ingestion.sampler import Sampler
from app.detection.format_detector import FormatDetector
from app.detection.validator import Validator
from app.ai.ai_assistant import AIAssistant
from app.parsers.generic_parser import GenericParser
from app.normalization.normalizer import Normalizer
from app.analytics.traffic import TrafficAnalyzer
from app.analytics.browser_stats import BrowserStats
from app.analytics.endpoints import EndpointAnalyzer
from app.security.rules import SecurityRules
from app.security.risk_score import RiskScorer
from app.security.ip_blocker import IPBlocker
from app.ml.feature_engineering import FeatureEngineer
from app.ml.anomaly_detector import AnomalyDetector
from app.database.database import Database, NumpyEncoder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LogSentinel",
    description="AI-Powered Intelligent Web Log Analyzer",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize components
file_reader = FileReader()
sampler = Sampler()
format_detector = FormatDetector()
validator = Validator()
ai_assistant = AIAssistant()
generic_parser = GenericParser()
normalizer = Normalizer()
traffic_analyzer = TrafficAnalyzer()
browser_stats = BrowserStats()
endpoint_analyzer = EndpointAnalyzer()
security_rules = SecurityRules()
risk_scorer = RiskScorer()
ip_blocker = IPBlocker(backend='local')
feature_engineer = FeatureEngineer()
anomaly_detector = AnomalyDetector()
database = Database()


@app.get("/")
async def root():
    """Serve the frontend dashboard."""
    html_path = "app/dashboard/index.html"
    try:
        return FileResponse(html_path)
    except:
        return {
            "name": "LogSentinel",
            "version": "2.0.0",
            "description": "AI-Powered Intelligent Web Log Analyzer"
        }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/status")
async def api_status():
    """API status with database stats."""
    db_stats = database.get_stats()
    ai_info = ai_assistant.get_provider_info()
    
    return {
        "status": "online",
        "version": "2.0.0",
        "database": db_stats,
        "ai_provider": ai_info,
        "features": [
            "Format Detection",
            "AI-Assisted Parsing",
            "Normalization",
            "Traffic Analytics",
            "Browser Stats",
            "Endpoint Analysis",
            "Security Rules",
            "ML Anomaly Detection",
            "Risk Scoring",
            "Database Storage",
            "Export (CSV/JSON)",
            "IP Blocking"
        ]
    }


@app.post("/analyze")
async def analyze_log(file: UploadFile = File(...)):
    """
    Main endpoint - Analyze a log file.
    """
    try:
        # Step 1: Read file
        logger.info(f"Reading file: {file.filename}")
        content, metadata = file_reader.read_uploaded_file(
            await file.read(), 
            file.filename
        )
        
        # Step 2: Collect sample
        logger.info("Collecting sample...")
        sample_lines = sampler.collect_sample(content)
        
        # Step 3: Detect format
        logger.info("Detecting format...")
        format_result = format_detector.detect_format(sample_lines)
        
        # Step 4: Get parser config
        if format_result.is_known:
            logger.info(f"Known format: {format_result.format_name}")
            config = format_result.parser_config
        else:
            logger.info("Unknown format - asking AI...")
            config = ai_assistant.suggest_parser_config(
                sample_lines, 
                format_result.sample_analysis
            )
        
        # Step 5: Validate config
        logger.info("Validating config...")
        is_valid, errors = validator.validate_config(config, sample_lines)
        
        if not is_valid:
            logger.warning(f"Validation failed: {errors}")
            # sample_analysis may be None for known formats — compute it as fallback
            sample_analysis = format_result.sample_analysis or format_detector._analyze_unknown_format(sample_lines)
            config = ai_assistant.suggest_parser_config(
                sample_lines,
                sample_analysis
            )
            is_valid, errors = validator.validate_config(config, sample_lines)
            
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not parse log file: {errors[:3]}"
                )
        
        # Step 6: Parse entire file
        logger.info("Parsing entire file...")
        parsed_df = generic_parser.parse(content, config)
        
        # Step 7: Normalize
        logger.info("Normalizing events...")
        normalized_df = normalizer.normalize(parsed_df)
        
        # Step 8: Traffic analytics
        logger.info("Running traffic analytics...")
        traffic_stats = traffic_analyzer.analyze(normalized_df)
        
        # Step 8b: Browser stats
        logger.info("Running browser stats...")
        browser_results = browser_stats.analyze(normalized_df)
        
        # Step 8c: Endpoint analytics
        logger.info("Running endpoint analytics...")
        endpoint_results = endpoint_analyzer.analyze(normalized_df)
        
        # Step 9: Security rules
        logger.info("Running security rules...")
        security_threats = security_rules.detect_threats(normalized_df)
        
        # Step 10: ML anomaly detection
        logger.info("Running ML anomaly detection...")
        feature_df = feature_engineer.create_features(normalized_df)
        feature_cols = feature_engineer.get_feature_columns(feature_df)
        anomaly_results, model_info = anomaly_detector.train_and_predict(feature_df, feature_cols)
        
        ml_anomalies = {
            'total_anomalies': int(anomaly_results['is_anomaly'].sum()),
            'anomaly_percentage': float(anomaly_results['is_anomaly'].mean() * 100),
            'model_info': model_info,
            'top_anomalies': anomaly_results[anomaly_results['is_anomaly'] == 1]
                .nlargest(10, 'anomaly_score')[['ip', 'total_requests', 'error_rate', 'anomaly_score']]
                .to_dict('records')
        }
        
        # Step 11: Risk score
        logger.info("Calculating risk score...")
        risk_score = risk_scorer.calculate_risk(
            security_threats,
            ml_anomalies,
            traffic_stats
        )
        
        # Step 12: Build result
        result = {
            'status': 'success',
            'file_info': metadata,
            'format_detected': {
                'name': format_result.format_name,
                'confidence': format_result.confidence,
                'is_known': format_result.is_known
            },
            'parsing_stats': generic_parser.get_stats(),
            'traffic': traffic_stats,
            'browser_stats': browser_results,
            'endpoint_stats': endpoint_results,
            'security': security_threats,
            'ml_anomalies': ml_anomalies,
            'risk_score': risk_score,
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 13: Save to database
        logger.info("Saving to database...")
        analysis_id = database.save_analysis(result)
        result['analysis_id'] = analysis_id
        
        logger.info(f"Analysis complete! ID: {analysis_id}")
        
        return JSONResponse(content=json.loads(json.dumps(result, cls=NumpyEncoder)))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# DATABASE ENDPOINTS
# ==========================================

@app.get("/history")
async def get_history(limit: int = Query(50, ge=1, le=100)):
    """Get analysis history."""
    analyses = database.get_all_analyses(limit)
    return {"analyses": analyses}


@app.get("/history/{analysis_id}")
async def get_analysis(analysis_id: int):
    """Get specific analysis by ID."""
    analysis = database.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


# ==========================================
# EXPORT ENDPOINTS
# ==========================================

@app.get("/export/json/{analysis_id}")
async def export_json(analysis_id: int):
    """Export analysis as JSON."""
    analysis = database.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return StreamingResponse(
        iter([json.dumps(analysis, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=analysis_{analysis_id}.json"}
    )


@app.get("/export/csv/{analysis_id}")
async def export_csv(analysis_id: int):
    """Export threats as CSV."""
    threats = database.get_threats_by_analysis(analysis_id)
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'analysis_id', 'threat_type', 'ip', 'url', 'timestamp'])
    writer.writeheader()
    writer.writerows(threats)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=threats_{analysis_id}.csv"}
    )


# ==========================================
# IP BLOCKING ENDPOINTS
# ==========================================

@app.post("/block-ip")
async def block_ip(ip: str, reason: str, risk_score: int = 0):
    """Block an IP address."""
    result = ip_blocker.block_ip(ip, reason, risk_score)
    database.block_ip(ip, reason, risk_score)
    return result


@app.post("/unblock-ip")
async def unblock_ip(ip: str):
    """Unblock an IP address."""
    result = ip_blocker.unblock_ip(ip)
    database.unblock_ip(ip)
    return result


@app.get("/blocked-ips")
async def get_blocked_ips():
    """Get list of blocked IPs."""
    blocked = database.get_blocked_ips()
    return {"blocked_ips": blocked}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
