"""
History Agent - Persistent History Record (PHR) Management
==========================================================

Provides skills for recording, querying, and managing the system's
persistent history records for auditing and learning.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseAgent, AgentContext, Skill

logger = logging.getLogger(__name__)

# PHR Schema
PHR_SCHEMA = {
    "id": "string",
    "timestamp": "datetime",
    "type": "enum[query, personalization, translation, code, content, auth, system]",
    "user_id": "string|null",
    "session_id": "string|null",
    "agent": "string",
    "skill": "string",
    "input_summary": "string",
    "output_summary": "string",
    "success": "boolean",
    "duration_ms": "number",
    "metadata": "object",
}


class HistoryAgent(BaseAgent):
    """
    Agent for managing Persistent History Records (PHR).

    Skills:
        - recordEvent: Log an event to the history
        - queryHistory: Query historical events
        - getAnalytics: Get usage analytics
        - exportHistory: Export history for analysis
    """

    def __init__(self, **kwargs):
        self._history_store: List[Dict[str, Any]] = []
        self._history_file = Path("history/phr_records.json")
        self._load_history()
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return "HistoryAgent"

    @property
    def description(self) -> str:
        return "Manages Persistent History Records (PHR) for system auditing, analytics, and learning"

    def _load_history(self):
        """Load history from file if exists."""
        try:
            if self._history_file.exists():
                with open(self._history_file, 'r', encoding='utf-8') as f:
                    self._history_store = json.load(f)
                logger.info(f"Loaded {len(self._history_store)} PHR records")
        except Exception as e:
            logger.warning(f"Could not load PHR history: {e}")
            self._history_store = []

    def _save_history(self):
        """Save history to file."""
        try:
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history_store[-1000:], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save PHR history: {e}")

    def _register_skills(self) -> None:
        """Register history management skills."""

        async def record_event_handler(
            context: AgentContext,
            event_type: str = "system",
            agent: str = None,
            skill: str = None,
            input_summary: str = None,
            output_summary: str = None,
            success: bool = True,
            duration_ms: int = 0,
            metadata: Dict[str, Any] = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Record a new event to the history."""
            phr_record = {
                "id": f"phr-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                "timestamp": datetime.utcnow().isoformat(),
                "type": event_type,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "agent": agent or "unknown",
                "skill": skill or "unknown",
                "input_summary": (input_summary or "")[:500],
                "output_summary": (output_summary or "")[:500],
                "success": success,
                "duration_ms": duration_ms,
                "metadata": metadata or {},
            }

            self._history_store.append(phr_record)
            self._save_history()

            logger.info(f"PHR recorded: {phr_record['id']} - {event_type}/{agent}/{skill}")
            return {"recorded": True, "phr_id": phr_record["id"]}

        self.register_skill(Skill(
            name="recordEvent",
            description="Record an event to the Persistent History Record",
            handler=record_event_handler,
            output_type="phr_record",
        ))

        async def query_history_handler(
            context: AgentContext,
            event_type: str = None,
            agent: str = None,
            user_id: str = None,
            limit: int = 50,
            offset: int = 0,
            start_date: str = None,
            end_date: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Query historical events with filters."""
            results = self._history_store.copy()

            # Apply filters
            if event_type:
                results = [r for r in results if r.get("type") == event_type]
            if agent:
                results = [r for r in results if r.get("agent") == agent]
            if user_id:
                results = [r for r in results if r.get("user_id") == user_id]
            if start_date:
                results = [r for r in results if r.get("timestamp", "") >= start_date]
            if end_date:
                results = [r for r in results if r.get("timestamp", "") <= end_date]

            # Sort by timestamp descending
            results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            # Apply pagination
            total = len(results)
            results = results[offset:offset + limit]

            return {
                "records": results,
                "total": total,
                "limit": limit,
                "offset": offset,
            }

        self.register_skill(Skill(
            name="queryHistory",
            description="Query historical events with filters",
            handler=query_history_handler,
            output_type="phr_query_result",
        ))

        async def get_analytics_handler(
            context: AgentContext,
            period: str = "day",  # day, week, month
            **kwargs
        ) -> Dict[str, Any]:
            """Get usage analytics from history."""
            from collections import Counter
            from datetime import timedelta

            now = datetime.utcnow()
            if period == "day":
                cutoff = now - timedelta(days=1)
            elif period == "week":
                cutoff = now - timedelta(weeks=1)
            else:
                cutoff = now - timedelta(days=30)

            cutoff_str = cutoff.isoformat()
            recent = [r for r in self._history_store if r.get("timestamp", "") >= cutoff_str]

            # Calculate analytics
            agent_counts = Counter(r.get("agent", "unknown") for r in recent)
            skill_counts = Counter(r.get("skill", "unknown") for r in recent)
            type_counts = Counter(r.get("type", "unknown") for r in recent)
            success_count = sum(1 for r in recent if r.get("success"))

            avg_duration = 0
            durations = [r.get("duration_ms", 0) for r in recent if r.get("duration_ms")]
            if durations:
                avg_duration = sum(durations) / len(durations)

            unique_users = len(set(r.get("user_id") for r in recent if r.get("user_id")))
            unique_sessions = len(set(r.get("session_id") for r in recent if r.get("session_id")))

            return {
                "period": period,
                "total_events": len(recent),
                "success_rate": success_count / len(recent) if recent else 0,
                "avg_duration_ms": avg_duration,
                "unique_users": unique_users,
                "unique_sessions": unique_sessions,
                "by_agent": dict(agent_counts.most_common(10)),
                "by_skill": dict(skill_counts.most_common(10)),
                "by_type": dict(type_counts.most_common(10)),
            }

        self.register_skill(Skill(
            name="getAnalytics",
            description="Get usage analytics from history",
            handler=get_analytics_handler,
            output_type="analytics",
        ))

        async def export_history_handler(
            context: AgentContext,
            format: str = "json",
            limit: int = 1000,
            **kwargs
        ) -> Dict[str, Any]:
            """Export history for external analysis."""
            records = self._history_store[-limit:]

            if format == "json":
                return {
                    "format": "json",
                    "count": len(records),
                    "data": records,
                }
            elif format == "csv":
                # Create CSV-like structure
                headers = ["id", "timestamp", "type", "agent", "skill", "success", "duration_ms"]
                rows = [[r.get(h, "") for h in headers] for r in records]
                return {
                    "format": "csv",
                    "count": len(records),
                    "headers": headers,
                    "rows": rows,
                }
            else:
                return {"error": f"Unsupported format: {format}"}

        self.register_skill(Skill(
            name="exportHistory",
            description="Export history for external analysis",
            handler=export_history_handler,
            output_type="export",
        ))

        async def get_user_history_handler(
            context: AgentContext,
            limit: int = 20,
            **kwargs
        ) -> Dict[str, Any]:
            """Get history for the current user."""
            if not context.user_id:
                return {"records": [], "message": "No user context provided"}

            user_records = [
                r for r in self._history_store
                if r.get("user_id") == context.user_id
            ]
            user_records.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return {
                "user_id": context.user_id,
                "total_events": len(user_records),
                "recent_events": user_records[:limit],
            }

        self.register_skill(Skill(
            name="getUserHistory",
            description="Get history for the current user",
            handler=get_user_history_handler,
            required_context=["user_id"],
            output_type="user_history",
        ))
