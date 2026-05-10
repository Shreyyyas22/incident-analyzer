"""
AI Analysis Service — builds prompts, calls AI, stores results.
"""
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.services.ai_provider import get_ai_provider
from app.repositories import incident_repo, log_repo
from app.models.incident import IncidentStatus

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are a senior SRE (Site Reliability Engineer) analyzing production incidents.
Respond ONLY in valid JSON format. Be concise and infrastructure-focused.
Do NOT include markdown fences or any text outside the JSON object.

Your response must follow this exact schema:
{
  "summary": "One-line summary of what happened",
  "root_cause": "Technical explanation of the root cause",
  "severity": "P1 or P2 or P3",
  "contributing_factors": ["factor 1", "factor 2"],
  "suggested_fixes": ["fix 1", "fix 2"],
  "confidence_score": 0.85
}

Severity guide:
- P1: Complete outage, data loss, or security breach
- P2: Partial degradation, high error rate, significant latency
- P3: Minor issues, warnings, non-critical errors"""


def build_analysis_prompt(
    service_name: str,
    environment: str,
    incident_created_at: datetime,
    error_logs: list,
    warning_logs: list,
) -> str:
    """Build a structured user prompt with incident context for the AI."""
    error_count = len(error_logs)
    
    error_messages = "\n".join(
        [f"  [{log.timestamp}] [{log.log_level.value}] {log.message}" for log in error_logs]
    ) or "  (no error logs found)"

    warning_messages = "\n".join(
        [f"  [{log.timestamp}] [{log.log_level.value}] {log.message}" for log in warning_logs]
    ) or "  (no warning logs found)"

    return f"""Analyze this production incident:

SERVICE: {service_name}
ENVIRONMENT: {environment}
INCIDENT STARTED: {incident_created_at.isoformat()}
ERROR COUNT: {error_count}

=== RECENT ERROR LOGS (most recent first, last 20) ===
{error_messages}

=== WARNING LOGS (5 minutes before incident) ===
{warning_messages}

Provide your analysis as a JSON object following the schema in your instructions."""


async def analyze_incident(session: AsyncSession, incident_id: str) -> dict | None:
    """
    Full analysis pipeline:
    1. Fetch incident and related context
    2. Build prompt
    3. Call AI
    4. Store analysis
    """
    # 1. Fetch incident
    incident = await incident_repo.get_incident_by_id(session, incident_id)
    if not incident:
        logger.error("Incident not found for analysis", incident_id=incident_id)
        return None

    # Mark as ANALYZING
    await incident_repo.update_incident_status(session, incident_id, IncidentStatus.ANALYZING)

    # 2. Fetch context
    service = incident.service
    error_logs = await log_repo.get_recent_error_logs(session, incident.service_id, limit=20)
    warning_logs = await log_repo.get_warning_logs_before(
        session, incident.service_id, before_time=incident.created_at, minutes=5
    )

    # 3. Build prompt and call AI
    user_prompt = build_analysis_prompt(
        service_name=service.name,
        environment=service.environment,
        incident_created_at=incident.created_at,
        error_logs=error_logs,
        warning_logs=warning_logs,
    )

    try:
        provider = get_ai_provider()
        analysis = await provider.analyze(SYSTEM_PROMPT, user_prompt)
        logger.info("AI analysis completed", incident_id=incident_id, severity=analysis.get("severity"))
    except Exception as e:
        logger.error("AI analysis failed", incident_id=incident_id, error=str(e))
        # Revert to OPEN on failure so it can be retried
        await incident_repo.update_incident_status(session, incident_id, IncidentStatus.OPEN)
        raise

    # 4. Store analysis
    severity = analysis.get("severity")
    await incident_repo.update_incident_analysis(
        session, incident_id, analysis=analysis, severity=severity
    )

    return analysis
