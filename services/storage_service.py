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
        """
        Get file path for session.

        Note: Uses first 12 characters of UUID (48 bits of entropy) for filename.
        Collision probability is extremely low (~1 in 281 trillion per pair).
        For a system with 10,000 daily interviews, expected collision once per ~2.8 billion years.
        """
        date_dir = self._get_date_dir(date)
        return date_dir / f"{session_id[:12]}_session.json"

    def _get_evaluation_path(self, session_id: str, date: datetime = None) -> Path:
        """Get file path for evaluation (uses same prefix as session)"""
        date_dir = self._get_date_dir(date)
        return date_dir / f"{session_id[:12]}_evaluation.json"

    def _get_resume_path(self, session_id: str, extension: str, date: datetime = None) -> Path:
        """Get file path for resume file (uses same prefix as session)"""
        date_dir = self._get_date_dir(date)
        return date_dir / f"{session_id[:12]}_resume.{extension}"

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

    def save_resume_file(
        self,
        session_id: str,
        file_data: bytes,
        original_filename: str,
        date: datetime = None
    ) -> str:
        """
        Save candidate's resume file.

        Args:
            session_id: Session ID
            file_data: File bytes
            original_filename: Original file name (for extension)
            date: Date for file organization

        Returns:
            Path to saved file
        """
        # Get file extension from original filename with whitelist validation
        ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp'}
        raw_extension = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        extension = raw_extension if raw_extension in ALLOWED_EXTENSIONS else 'bin'

        path = self._get_resume_path(session_id, extension, date)

        # Write file with locking
        with file_lock(str(path)):
            with open(path, "wb") as f:
                f.write(file_data)

        return str(path)

    def get_resume_file_path(self, session_id: str, days: int = 30) -> Optional[str]:
        """
        Find resume file path by session ID prefix.

        Args:
            session_id: Session ID prefix (first 8 chars)
            days: Number of days to search back

        Returns:
            Path to resume file or None
        """
        from datetime import timedelta

        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if not date_dir.exists():
                continue

            # Look for resume file with any extension (using 12-char prefix)
            resume_files = list(date_dir.glob(f"{session_id[:12]}_resume.*"))

            if resume_files:
                return str(resume_files[0])

        return None

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
        offset: int = 0,
        grade_filter: str = None
    ) -> List[dict]:
        """
        Get recent sessions summary with pagination and optional grade filter.

        Args:
            days: Number of days to look back
            limit: Maximum number of results
            offset: Skip first N results
            grade_filter: Filter by grade (S, A, B, C) or None for all

        Returns:
            List of session summaries with evaluation info
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
                # Handle limit
                if count >= limit:
                    return summaries

                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Try to load evaluation for this session
                    session_prefix = file.stem.replace("_session", "")
                    eval_file = date_dir / f"{session_prefix}_evaluation.json"

                    grade = None
                    score = None
                    is_s_tier = False

                    if eval_file.exists():
                        try:
                            with open(eval_file, "r", encoding="utf-8") as ef:
                                eval_data = json.load(ef)
                            # Field is "decision_tier" not "grade", "total_score" not "overall_score"
                            grade = eval_data.get("decision_tier", None)
                            score = eval_data.get("total_score", None)
                            is_s_tier = eval_data.get("is_s_tier", False) or grade == "S"
                        except Exception:
                            pass

                    # Apply grade filter if specified
                    if grade_filter:
                        if grade != grade_filter:
                            continue

                    # Handle offset (skip) - after filter to get correct count
                    if skipped < offset:
                        skipped += 1
                        continue

                    summaries.append({
                        "session_id": data.get("session_id", "")[:12],
                        "candidate_name": data.get("candidate_name", "Unknown"),
                        "candidate_email": data.get("candidate_email", ""),
                        "status": data.get("status", "unknown"),
                        "turn_count": data.get("turn_count", 0),
                        "created_at": data.get("created_at", ""),
                        "date": date_str,
                        "file_path": str(file),
                        "grade": grade,
                        "score": score,
                        "is_s_tier": is_s_tier
                    })
                    count += 1
                except Exception:
                    continue

        return summaries

    def get_grade_counts(self, days: int = 7) -> dict:
        """
        Get count of sessions by grade.

        Args:
            days: Number of days to look back

        Returns:
            Dict with grade counts: {"S": n, "A": n, "B": n, "C": n, "pending": n}
        """
        from datetime import timedelta

        counts = {"S": 0, "A": 0, "B": 0, "C": 0, "pending": 0}
        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if not date_dir.exists():
                continue

            for session_file in date_dir.glob("*_session.json"):
                session_prefix = session_file.stem.replace("_session", "")
                eval_file = date_dir / f"{session_prefix}_evaluation.json"

                if eval_file.exists():
                    try:
                        with open(eval_file, "r", encoding="utf-8") as f:
                            eval_data = json.load(f)
                        # Field is "decision_tier" not "grade"
                        grade = eval_data.get("decision_tier", None)
                        if grade in counts:
                            counts[grade] += 1
                        else:
                            counts["pending"] += 1
                    except Exception:
                        counts["pending"] += 1
                else:
                    counts["pending"] += 1

        return counts

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

            # Look for session file with this prefix (supports both 8 and 12 char prefixes)
            session_files = list(date_dir.glob(f"{session_prefix}*_session.json"))

            if session_files:
                session_file = session_files[0]
                # Extract the actual prefix from the found file to match evaluation file
                actual_prefix = session_file.stem.replace("_session", "")
                eval_file = date_dir / f"{actual_prefix}_evaluation.json"

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

    def delete_session_by_date_str(self, session_id: str, date_str: str) -> bool:
        """
        Delete session by session ID prefix and date string.

        Args:
            session_id: Session ID prefix (first 12 chars)
            date_str: Date string in format "YYYY-MM-DD"

        Returns:
            True if deleted
        """
        date_dir = self.base_dir / date_str

        if not date_dir.exists():
            return False

        deleted = False

        # Delete session file
        session_files = list(date_dir.glob(f"{session_id[:12]}*_session.json"))
        for f in session_files:
            os.remove(f)
            deleted = True

        # Delete evaluation file
        eval_files = list(date_dir.glob(f"{session_id[:12]}*_evaluation.json"))
        for f in eval_files:
            os.remove(f)

        # Delete resume file
        resume_files = list(date_dir.glob(f"{session_id[:12]}*_resume.*"))
        for f in resume_files:
            os.remove(f)

        return deleted

    def clear_all_sessions(self, days: int = 7) -> int:
        """
        Clear all sessions within the specified date range.

        Args:
            days: Number of days to clear (default: 7)

        Returns:
            Number of sessions deleted
        """
        from datetime import timedelta

        count = 0
        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if not date_dir.exists():
                continue

            # Delete all session files
            for f in date_dir.glob("*_session.json"):
                os.remove(f)
                count += 1

            # Delete all evaluation files
            for f in date_dir.glob("*_evaluation.json"):
                os.remove(f)

            # Delete all resume files
            for f in date_dir.glob("*_resume.*"):
                os.remove(f)

        return count


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
