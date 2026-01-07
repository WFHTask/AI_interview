"""
Storage Service for Interview Data

Stores interview sessions and evaluations as JSON files.
Simple file-based storage for MVP.

Features:
- File locking for concurrent access safety
- Atomic writes to prevent corruption
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from config.settings import Settings
from models.schemas import InterviewSession, EvaluationResult
from utils.file_lock import file_lock, safe_write_json


class StorageService:
    """
    File-based storage service for interview data

    Structure:
    data/interviews/
    ├── 2024-01-15/
    │   ├── abc123_session.json
    │   └── abc123_evaluation.json
    └── 2024-01-16/
        └── ...
    """

    def __init__(self, base_dir: Path = None):
        """
        Initialize storage service

        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = Path(base_dir) if base_dir else Path(Settings.DATA_DIR)
        self._ensure_dir_exists()

    def _ensure_dir_exists(self) -> None:
        """Create base directory if not exists"""
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_date_dir(self, date: datetime = None) -> Path:
        """Get directory for specific date"""
        date = date or datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        date_dir = self.base_dir / date_str
        os.makedirs(date_dir, exist_ok=True)
        return date_dir

    def _get_session_path(self, session_id: str, date: datetime = None) -> Path:
        """Get file path for session"""
        date_dir = self._get_date_dir(date)
        return date_dir / f"{session_id[:8]}_session.json"

    def _get_evaluation_path(self, session_id: str, date: datetime = None) -> Path:
        """Get file path for evaluation"""
        date_dir = self._get_date_dir(date)
        return date_dir / f"{session_id[:8]}_evaluation.json"

    def save_session(self, session: InterviewSession) -> str:
        """
        Save interview session with file locking.

        Args:
            session: Interview session to save

        Returns:
            Path to saved file
        """
        path = self._get_session_path(session.session_id, session.created_at)

        # Convert to dict with datetime handling
        data = session.model_dump(mode="json")

        # Use safe write with locking
        safe_write_json(str(path), data)

        return str(path)

    def save_evaluation(
        self,
        session_id: str,
        evaluation: EvaluationResult,
        date: datetime = None
    ) -> str:
        """
        Save evaluation result with file locking.

        Args:
            session_id: Session ID
            evaluation: Evaluation result
            date: Date for file organization

        Returns:
            Path to saved file
        """
        path = self._get_evaluation_path(session_id, date)

        data = evaluation.model_dump(mode="json")

        # Use safe write with locking
        safe_write_json(str(path), data)

        return str(path)

    def load_session(self, session_id: str, date: datetime = None) -> Optional[InterviewSession]:
        """
        Load interview session with file locking.

        Args:
            session_id: Session ID
            date: Date to look in

        Returns:
            InterviewSession or None if not found
        """
        path = self._get_session_path(session_id, date)

        if not path.exists():
            return None

        with file_lock(str(path)):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

        return InterviewSession(**data)

    def load_evaluation(
        self,
        session_id: str,
        date: datetime = None
    ) -> Optional[EvaluationResult]:
        """
        Load evaluation result with file locking.

        Args:
            session_id: Session ID
            date: Date to look in

        Returns:
            EvaluationResult or None if not found
        """
        path = self._get_evaluation_path(session_id, date)

        if not path.exists():
            return None

        with file_lock(str(path)):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

        return EvaluationResult(**data)

    def list_sessions(self, date: datetime = None) -> List[str]:
        """
        List all session IDs for a date

        Args:
            date: Date to list (default: today)

        Returns:
            List of session IDs
        """
        date_dir = self._get_date_dir(date)

        if not date_dir.exists():
            return []

        sessions = []
        for file in date_dir.glob("*_session.json"):
            session_id = file.stem.replace("_session", "")
            sessions.append(session_id)

        return sessions

    def get_recent_sessions(
        self,
        days: int = 7,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Get recent sessions summary with pagination.

        Args:
            days: Number of days to look back
            limit: Maximum number of results
            offset: Skip first N results

        Returns:
            List of session summaries
        """
        from datetime import timedelta

        summaries = []
        today = datetime.now().date()
        count = 0
        skipped = 0

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            date_dir = self.base_dir / date_str
            if not date_dir.exists():
                continue

            # Get files sorted by modification time (newest first)
            files = sorted(
                date_dir.glob("*_session.json"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )

            for file in files:
                # Handle offset (skip)
                if skipped < offset:
                    skipped += 1
                    continue

                # Handle limit
                if count >= limit:
                    return summaries

                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    summaries.append({
                        "session_id": data.get("session_id", "")[:8],
                        "candidate_name": data.get("candidate_name", "Unknown"),
                        "candidate_email": data.get("candidate_email", ""),
                        "status": data.get("status", "unknown"),
                        "turn_count": data.get("turn_count", 0),
                        "created_at": data.get("created_at", ""),
                        "date": date_str,
                        "file_path": str(file)
                    })
                    count += 1
                except Exception:
                    continue

        return summaries

    def get_session_count(self, days: int = 7) -> int:
        """
        Get total count of sessions in date range.

        Args:
            days: Number of days to look back

        Returns:
            Total session count
        """
        from datetime import timedelta

        count = 0
        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if date_dir.exists():
                count += len(list(date_dir.glob("*_session.json")))

        return count

    def find_session_by_prefix(self, session_prefix: str, days: int = 30) -> Optional[tuple]:
        """
        Find session by ID prefix (first 8 chars).

        Args:
            session_prefix: First 8 characters of session ID
            days: Number of days to search back

        Returns:
            Tuple of (InterviewSession, EvaluationResult) or None
        """
        from datetime import timedelta

        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if not date_dir.exists():
                continue

            # Look for session file with this prefix
            session_files = list(date_dir.glob(f"{session_prefix}_session.json"))

            if session_files:
                session_file = session_files[0]
                eval_file = date_dir / f"{session_prefix}_evaluation.json"

                try:
                    # Load session
                    with file_lock(str(session_file)):
                        with open(session_file, "r", encoding="utf-8") as f:
                            session_data = json.load(f)
                    session = InterviewSession(**session_data)

                    # Load evaluation if exists
                    evaluation = None
                    if eval_file.exists():
                        with file_lock(str(eval_file)):
                            with open(eval_file, "r", encoding="utf-8") as f:
                                eval_data = json.load(f)
                        evaluation = EvaluationResult(**eval_data)

                    return session, evaluation

                except Exception:
                    continue

        return None

    def delete_session(self, session_id: str, date: datetime = None) -> bool:
        """
        Delete session and its evaluation

        Args:
            session_id: Session ID
            date: Date of session

        Returns:
            True if deleted
        """
        session_path = self._get_session_path(session_id, date)
        eval_path = self._get_evaluation_path(session_id, date)

        deleted = False

        if session_path.exists():
            os.remove(session_path)
            deleted = True

        if eval_path.exists():
            os.remove(eval_path)
            deleted = True

        return deleted


# Singleton instance
storage_service = StorageService()


def save_interview_complete(
    session: InterviewSession,
    evaluation: EvaluationResult
) -> tuple[str, str]:
    """
    Save complete interview (session + evaluation)

    Args:
        session: Interview session
        evaluation: Evaluation result

    Returns:
        Tuple of (session_path, evaluation_path)
    """
    session_path = storage_service.save_session(session)
    eval_path = storage_service.save_evaluation(
        session.session_id,
        evaluation,
        session.created_at
    )

    return session_path, eval_path
