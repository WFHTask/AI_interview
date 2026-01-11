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
                        "candidate_phone": data.get("candidate_phone", ""),
                        "candidate_wechat": data.get("candidate_wechat", ""),
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

    def export_sessions_json(self, days: int = 7, grade_filter: str = None) -> str:
        """
        Export all sessions as JSON string.

        Args:
            days: Number of days to export
            grade_filter: Filter by grade (S, A, B, C) or None for all

        Returns:
            JSON string with all session and evaluation data
        """
        from datetime import timedelta

        export_data = {
            "export_date": datetime.now().isoformat(),
            "days_range": days,
            "grade_filter": grade_filter,
            "sessions": []
        }

        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if not date_dir.exists():
                continue

            for session_file in date_dir.glob("*_session.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)

                    # Try to load evaluation
                    session_prefix = session_file.stem.replace("_session", "")
                    eval_file = date_dir / f"{session_prefix}_evaluation.json"

                    eval_data = None
                    if eval_file.exists():
                        try:
                            with open(eval_file, "r", encoding="utf-8") as ef:
                                eval_data = json.load(ef)
                        except Exception:
                            pass

                    # Apply grade filter
                    if grade_filter:
                        session_grade = eval_data.get("decision_tier") if eval_data else None
                        if session_grade != grade_filter:
                            continue

                    export_data["sessions"].append({
                        "date": date_str,
                        "session": session_data,
                        "evaluation": eval_data
                    })
                except Exception:
                    continue

        return json.dumps(export_data, ensure_ascii=False, indent=2, default=str)

    def export_sessions_html(self, days: int = 7, grade_filter: str = None) -> str:
        """
        Export all sessions as HTML string.

        Args:
            days: Number of days to export
            grade_filter: Filter by grade (S, A, B, C) or None for all

        Returns:
            HTML string with formatted interview records
        """
        from datetime import timedelta

        today = datetime.now().date()
        filter_text = f" | 等级: {grade_filter}" if grade_filter else ""

        html_parts = ["""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiVerse 面试历史导出</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #0D9488; border-bottom: 2px solid #0D9488; padding-bottom: 10px; }
        .session { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .session-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .candidate-name { font-size: 1.25rem; font-weight: 600; color: #1E293B; }
        .grade { padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.875rem; }
        .grade-S { background: linear-gradient(135deg, #FCD34D, #F59E0B); color: #78350F; }
        .grade-A { background: linear-gradient(135deg, #34D399, #10B981); color: #064E3B; }
        .grade-B { background: linear-gradient(135deg, #60A5FA, #3B82F6); color: #1E3A8A; }
        .grade-C { background: linear-gradient(135deg, #F87171, #EF4444); color: #7F1D1D; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 15px; }
        .info-item { color: #64748B; font-size: 0.875rem; }
        .info-label { font-weight: 500; color: #475569; }
        .score { font-size: 2rem; font-weight: 700; color: #0D9488; }
        .summary { background: #F8FAFC; padding: 15px; border-radius: 8px; margin-top: 15px; }
        .chat-history { margin-top: 15px; border-top: 1px solid #E2E8F0; padding-top: 15px; }
        .message { margin-bottom: 10px; padding: 10px; border-radius: 8px; }
        .message-user { background: #E0F2FE; margin-left: 20px; }
        .message-model { background: #ECFDF5; margin-right: 20px; }
        .message-role { font-weight: 600; font-size: 0.75rem; color: #64748B; margin-bottom: 4px; }
        .strengths { color: #059669; }
        .red-flags { color: #DC2626; }
        .list-item { margin: 4px 0; padding-left: 16px; position: relative; }
        .list-item::before { content: "•"; position: absolute; left: 0; }
    </style>
</head>
<body>
    <h1>VoiVerse 面试历史导出</h1>
    <p style="color: #64748B;">导出时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + f""" | 数据范围: 最近 {days} 天{filter_text}</p>
"""]

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if not date_dir.exists():
                continue

            for session_file in date_dir.glob("*_session.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)

                    # Try to load evaluation
                    session_prefix = session_file.stem.replace("_session", "")
                    eval_file = date_dir / f"{session_prefix}_evaluation.json"

                    eval_data = None
                    if eval_file.exists():
                        try:
                            with open(eval_file, "r", encoding="utf-8") as ef:
                                eval_data = json.load(ef)
                        except Exception:
                            pass

                    # Apply grade filter
                    if grade_filter:
                        session_grade = eval_data.get("decision_tier") if eval_data else None
                        if session_grade != grade_filter:
                            continue

                    # Build session HTML
                    candidate_name = session_data.get("candidate_name", "Unknown")
                    candidate_email = session_data.get("candidate_email", "")
                    candidate_phone = session_data.get("candidate_phone", "")
                    candidate_wechat = session_data.get("candidate_wechat", "")
                    turn_count = session_data.get("turn_count", 0)
                    created_at = session_data.get("created_at", "")

                    grade = eval_data.get("decision_tier", "") if eval_data else ""
                    score = eval_data.get("total_score", "") if eval_data else ""
                    summary = eval_data.get("summary", "") if eval_data else ""
                    strengths = eval_data.get("key_strengths", []) if eval_data else []
                    red_flags = eval_data.get("red_flags", []) if eval_data else []

                    grade_class = f"grade-{grade}" if grade else ""

                    strengths_html = "".join([f'<div class="list-item">{s}</div>' for s in strengths])
                    red_flags_html = "".join([f'<div class="list-item">{r}</div>' for r in red_flags])

                    # Chat history
                    chat_html = ""
                    for msg in session_data.get("chat_history", []):
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        role_label = "面试官" if role == "model" else "候选人"
                        msg_class = "message-model" if role == "model" else "message-user"
                        chat_html += f'''
                        <div class="message {msg_class}">
                            <div class="message-role">{role_label}</div>
                            <div>{content}</div>
                        </div>'''

                    html_parts.append(f'''
    <div class="session">
        <div class="session-header">
            <span class="candidate-name">{candidate_name}</span>
            <span class="grade {grade_class}">{grade} {score}分</span>
        </div>
        <div class="info-grid">
            <div class="info-item"><span class="info-label">邮箱:</span> {candidate_email}</div>
            <div class="info-item"><span class="info-label">电话:</span> {candidate_phone}</div>
            <div class="info-item"><span class="info-label">微信:</span> {candidate_wechat}</div>
            <div class="info-item"><span class="info-label">面试时间:</span> {created_at}</div>
            <div class="info-item"><span class="info-label">对话轮次:</span> {turn_count} 轮</div>
        </div>
        {f'<div class="summary"><strong>评估总结:</strong> {summary}</div>' if summary else ''}
        <div style="display: flex; gap: 20px; margin-top: 15px;">
            <div class="strengths" style="flex: 1;"><strong>核心亮点:</strong>{strengths_html or '<div class="list-item">无</div>'}</div>
            <div class="red-flags" style="flex: 1;"><strong>关注点:</strong>{red_flags_html or '<div class="list-item">无</div>'}</div>
        </div>
        <details class="chat-history">
            <summary style="cursor: pointer; font-weight: 600; color: #0D9488;">查看完整对话记录</summary>
            {chat_html}
        </details>
    </div>''')
                except Exception:
                    continue

        html_parts.append("""
</body>
</html>""")

        return "".join(html_parts)

    def export_single_session_json(self, session_id: str) -> str:
        """Export a single session as JSON string"""
        from datetime import timedelta

        today = datetime.now().date()

        # Search in recent 90 days
        for i in range(90):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if not date_dir.exists():
                continue

            session_file = date_dir / f"{session_id}_session.json"
            if session_file.exists():
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)

                    eval_file = date_dir / f"{session_id}_evaluation.json"
                    eval_data = None
                    if eval_file.exists():
                        with open(eval_file, "r", encoding="utf-8") as ef:
                            eval_data = json.load(ef)

                    export_data = {
                        "export_date": datetime.now().isoformat(),
                        "session": session_data,
                        "evaluation": eval_data
                    }
                    return json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
                except Exception:
                    return None

        return None

    def export_single_session_html(self, session_id: str) -> str:
        """Export a single session as HTML string"""
        from datetime import timedelta

        today = datetime.now().date()

        # Search in recent 90 days
        for i in range(90):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_dir = self.base_dir / date_str

            if not date_dir.exists():
                continue

            session_file = date_dir / f"{session_id}_session.json"
            if session_file.exists():
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)

                    eval_file = date_dir / f"{session_id}_evaluation.json"
                    eval_data = None
                    if eval_file.exists():
                        with open(eval_file, "r", encoding="utf-8") as ef:
                            eval_data = json.load(ef)

                    candidate_name = session_data.get("candidate_name", "Unknown")
                    candidate_email = session_data.get("candidate_email", "")
                    candidate_phone = session_data.get("candidate_phone", "")
                    candidate_wechat = session_data.get("candidate_wechat", "")
                    turn_count = session_data.get("turn_count", 0)
                    created_at = session_data.get("created_at", "")

                    grade = eval_data.get("decision_tier", "") if eval_data else ""
                    score = eval_data.get("total_score", "") if eval_data else ""
                    summary = eval_data.get("summary", "") if eval_data else ""
                    strengths = eval_data.get("key_strengths", []) if eval_data else []
                    red_flags = eval_data.get("red_flags", []) if eval_data else []

                    grade_class = f"grade-{grade}" if grade else ""
                    strengths_html = "".join([f'<div class="list-item">{s}</div>' for s in strengths])
                    red_flags_html = "".join([f'<div class="list-item">{r}</div>' for r in red_flags])

                    chat_html = ""
                    for msg in session_data.get("chat_history", []):
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        role_label = "面试官" if role == "model" else "候选人"
                        msg_class = "message-model" if role == "model" else "message-user"
                        chat_html += f'''
                        <div class="message {msg_class}">
                            <div class="message-role">{role_label}</div>
                            <div>{content}</div>
                        </div>'''

                    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{candidate_name} - 面试记录</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #0D9488; border-bottom: 2px solid #0D9488; padding-bottom: 10px; }}
        .session {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .session-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .candidate-name {{ font-size: 1.25rem; font-weight: 600; color: #1E293B; }}
        .grade {{ padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.875rem; }}
        .grade-S {{ background: linear-gradient(135deg, #FCD34D, #F59E0B); color: #78350F; }}
        .grade-A {{ background: linear-gradient(135deg, #34D399, #10B981); color: #064E3B; }}
        .grade-B {{ background: linear-gradient(135deg, #60A5FA, #3B82F6); color: #1E3A8A; }}
        .grade-C {{ background: linear-gradient(135deg, #F87171, #EF4444); color: #7F1D1D; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 15px; }}
        .info-item {{ color: #64748B; font-size: 0.875rem; }}
        .info-label {{ font-weight: 500; color: #475569; }}
        .summary {{ background: #F8FAFC; padding: 15px; border-radius: 8px; margin-top: 15px; }}
        .chat-history {{ margin-top: 15px; border-top: 1px solid #E2E8F0; padding-top: 15px; }}
        .message {{ margin-bottom: 10px; padding: 10px; border-radius: 8px; }}
        .message-user {{ background: #E0F2FE; margin-left: 20px; }}
        .message-model {{ background: #ECFDF5; margin-right: 20px; }}
        .message-role {{ font-weight: 600; font-size: 0.75rem; color: #64748B; margin-bottom: 4px; }}
        .strengths {{ color: #059669; }}
        .red-flags {{ color: #DC2626; }}
        .list-item {{ margin: 4px 0; padding-left: 16px; position: relative; }}
        .list-item::before {{ content: "•"; position: absolute; left: 0; }}
    </style>
</head>
<body>
    <h1>{candidate_name} - 面试记录</h1>
    <p style="color: #64748B;">导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <div class="session">
        <div class="session-header">
            <span class="candidate-name">{candidate_name}</span>
            <span class="grade {grade_class}">{grade} {score}分</span>
        </div>
        <div class="info-grid">
            <div class="info-item"><span class="info-label">邮箱:</span> {candidate_email}</div>
            <div class="info-item"><span class="info-label">电话:</span> {candidate_phone}</div>
            <div class="info-item"><span class="info-label">微信:</span> {candidate_wechat}</div>
            <div class="info-item"><span class="info-label">面试时间:</span> {created_at}</div>
            <div class="info-item"><span class="info-label">对话轮次:</span> {turn_count} 轮</div>
        </div>
        {f'<div class="summary"><strong>评估总结:</strong> {summary}</div>' if summary else ''}
        <div style="display: flex; gap: 20px; margin-top: 15px;">
            <div class="strengths" style="flex: 1;"><strong>核心亮点:</strong>{strengths_html or '<div class="list-item">无</div>'}</div>
            <div class="red-flags" style="flex: 1;"><strong>关注点:</strong>{red_flags_html or '<div class="list-item">无</div>'}</div>
        </div>
        <div class="chat-history">
            <strong style="color: #0D9488;">完整对话记录</strong>
            {chat_html}
        </div>
    </div>
</body>
</html>"""
                    return html
                except Exception:
                    return None

        return None

    def export_sessions_by_date_json(self, date_str: str, grade_filter: str = None) -> str:
        """Export sessions for a specific date as JSON string"""
        date_dir = self.base_dir / date_str

        export_data = {
            "export_date": datetime.now().isoformat(),
            "target_date": date_str,
            "grade_filter": grade_filter,
            "sessions": []
        }

        if not date_dir.exists():
            return json.dumps(export_data, ensure_ascii=False, indent=2, default=str)

        for session_file in date_dir.glob("*_session.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)

                session_prefix = session_file.stem.replace("_session", "")
                eval_file = date_dir / f"{session_prefix}_evaluation.json"

                eval_data = None
                if eval_file.exists():
                    try:
                        with open(eval_file, "r", encoding="utf-8") as ef:
                            eval_data = json.load(ef)
                    except Exception:
                        pass

                # Apply grade filter
                if grade_filter:
                    session_grade = eval_data.get("decision_tier") if eval_data else None
                    if session_grade != grade_filter:
                        continue

                export_data["sessions"].append({
                    "date": date_str,
                    "session": session_data,
                    "evaluation": eval_data
                })
            except Exception:
                continue

        return json.dumps(export_data, ensure_ascii=False, indent=2, default=str)

    def export_sessions_by_date_html(self, date_str: str, grade_filter: str = None) -> str:
        """Export sessions for a specific date as HTML string"""
        date_dir = self.base_dir / date_str
        filter_text = f" | 等级: {grade_filter}" if grade_filter else ""

        html_parts = [f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiVerse 面试记录 - {date_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #0D9488; border-bottom: 2px solid #0D9488; padding-bottom: 10px; }}
        .session {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .session-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .candidate-name {{ font-size: 1.25rem; font-weight: 600; color: #1E293B; }}
        .grade {{ padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.875rem; }}
        .grade-S {{ background: linear-gradient(135deg, #FCD34D, #F59E0B); color: #78350F; }}
        .grade-A {{ background: linear-gradient(135deg, #34D399, #10B981); color: #064E3B; }}
        .grade-B {{ background: linear-gradient(135deg, #60A5FA, #3B82F6); color: #1E3A8A; }}
        .grade-C {{ background: linear-gradient(135deg, #F87171, #EF4444); color: #7F1D1D; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 15px; }}
        .info-item {{ color: #64748B; font-size: 0.875rem; }}
        .info-label {{ font-weight: 500; color: #475569; }}
        .summary {{ background: #F8FAFC; padding: 15px; border-radius: 8px; margin-top: 15px; }}
        .chat-history {{ margin-top: 15px; border-top: 1px solid #E2E8F0; padding-top: 15px; }}
        .message {{ margin-bottom: 10px; padding: 10px; border-radius: 8px; }}
        .message-user {{ background: #E0F2FE; margin-left: 20px; }}
        .message-model {{ background: #ECFDF5; margin-right: 20px; }}
        .message-role {{ font-weight: 600; font-size: 0.75rem; color: #64748B; margin-bottom: 4px; }}
        .strengths {{ color: #059669; }}
        .red-flags {{ color: #DC2626; }}
        .list-item {{ margin: 4px 0; padding-left: 16px; position: relative; }}
        .list-item::before {{ content: "•"; position: absolute; left: 0; }}
    </style>
</head>
<body>
    <h1>VoiVerse 面试记录 - {date_str}</h1>
    <p style="color: #64748B;">导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{filter_text}</p>
"""]

        if not date_dir.exists():
            html_parts.append("<p>该日期无面试记录</p>")
        else:
            count = 0
            for session_file in date_dir.glob("*_session.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)

                    session_prefix = session_file.stem.replace("_session", "")
                    eval_file = date_dir / f"{session_prefix}_evaluation.json"

                    eval_data = None
                    if eval_file.exists():
                        try:
                            with open(eval_file, "r", encoding="utf-8") as ef:
                                eval_data = json.load(ef)
                        except Exception:
                            pass

                    # Apply grade filter
                    if grade_filter:
                        session_grade = eval_data.get("decision_tier") if eval_data else None
                        if session_grade != grade_filter:
                            continue

                    # Build session HTML
                    candidate_name = session_data.get("candidate_name", "Unknown")
                    candidate_email = session_data.get("candidate_email", "")
                    candidate_phone = session_data.get("candidate_phone", "")
                    candidate_wechat = session_data.get("candidate_wechat", "")
                    turn_count = session_data.get("turn_count", 0)
                    created_at = session_data.get("created_at", "")

                    grade = eval_data.get("decision_tier", "") if eval_data else ""
                    score = eval_data.get("total_score", "") if eval_data else ""
                    summary = eval_data.get("summary", "") if eval_data else ""
                    strengths = eval_data.get("key_strengths", []) if eval_data else []
                    red_flags = eval_data.get("red_flags", []) if eval_data else []

                    grade_class = f"grade-{grade}" if grade else ""
                    strengths_html = "".join([f'<div class="list-item">{s}</div>' for s in strengths])
                    red_flags_html = "".join([f'<div class="list-item">{r}</div>' for r in red_flags])

                    chat_html = ""
                    for msg in session_data.get("chat_history", []):
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        role_label = "面试官" if role == "model" else "候选人"
                        msg_class = "message-model" if role == "model" else "message-user"
                        chat_html += f'''
                        <div class="message {msg_class}">
                            <div class="message-role">{role_label}</div>
                            <div>{content}</div>
                        </div>'''

                    html_parts.append(f'''
    <div class="session">
        <div class="session-header">
            <span class="candidate-name">{candidate_name}</span>
            <span class="grade {grade_class}">{grade} {score}分</span>
        </div>
        <div class="info-grid">
            <div class="info-item"><span class="info-label">邮箱:</span> {candidate_email}</div>
            <div class="info-item"><span class="info-label">电话:</span> {candidate_phone}</div>
            <div class="info-item"><span class="info-label">微信:</span> {candidate_wechat}</div>
            <div class="info-item"><span class="info-label">面试时间:</span> {created_at}</div>
            <div class="info-item"><span class="info-label">对话轮次:</span> {turn_count} 轮</div>
        </div>
        {f'<div class="summary"><strong>评估总结:</strong> {summary}</div>' if summary else ''}
        <div style="display: flex; gap: 20px; margin-top: 15px;">
            <div class="strengths" style="flex: 1;"><strong>核心亮点:</strong>{strengths_html or '<div class="list-item">无</div>'}</div>
            <div class="red-flags" style="flex: 1;"><strong>关注点:</strong>{red_flags_html or '<div class="list-item">无</div>'}</div>
        </div>
        <details class="chat-history">
            <summary style="cursor: pointer; font-weight: 600; color: #0D9488;">查看完整对话记录</summary>
            {chat_html}
        </details>
    </div>''')
                    count += 1
                except Exception:
                    continue

            if count == 0:
                html_parts.append("<p>该日期无符合条件的面试记录</p>")

        html_parts.append("""
</body>
</html>""")

        return "".join(html_parts)

    def export_sessions_by_date_zip(self, date_str: str, grade_filter: str = None, export_format: str = "both") -> bytes:
        """
        Export sessions for a specific date as ZIP archive.
        Each session is exported as individual JSON and/or HTML files.

        Args:
            date_str: Date string in format "YYYY-MM-DD"
            grade_filter: Filter by grade (S, A, B, C) or None for all
            export_format: "json", "html", or "both"

        Returns:
            ZIP file bytes
        """
        import io
        import zipfile

        date_dir = self.base_dir / date_str

        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if not date_dir.exists():
                # Add empty readme if no data
                zip_file.writestr("README.txt", f"该日期 ({date_str}) 无面试记录")
                zip_buffer.seek(0)
                return zip_buffer.getvalue()

            count = 0
            for session_file in date_dir.glob("*_session.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)

                    session_prefix = session_file.stem.replace("_session", "")
                    eval_file = date_dir / f"{session_prefix}_evaluation.json"

                    eval_data = None
                    if eval_file.exists():
                        try:
                            with open(eval_file, "r", encoding="utf-8") as ef:
                                eval_data = json.load(ef)
                        except Exception:
                            pass

                    # Apply grade filter
                    if grade_filter:
                        session_grade = eval_data.get("decision_tier") if eval_data else None
                        if session_grade != grade_filter:
                            continue

                    # Get candidate name for filename
                    candidate_name = session_data.get("candidate_name", "Unknown")
                    # Sanitize filename
                    safe_name = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_name = safe_name[:30] if safe_name else "unknown"

                    grade = eval_data.get("decision_tier", "pending") if eval_data else "pending"

                    # Create JSON content for this session
                    json_content = json.dumps({
                        "session": session_data,
                        "evaluation": eval_data
                    }, ensure_ascii=False, indent=2, default=str)

                    # Add files to ZIP based on format
                    file_prefix = f"{grade}_{safe_name}_{session_prefix[:8]}"

                    if export_format in ("json", "both"):
                        zip_file.writestr(f"{file_prefix}.json", json_content.encode('utf-8'))

                    if export_format in ("html", "both"):
                        html_content = self._generate_single_session_html(
                            session_data, eval_data, date_str
                        )
                        zip_file.writestr(f"{file_prefix}.html", html_content.encode('utf-8'))

                    count += 1
                except Exception:
                    continue

            if count == 0:
                zip_file.writestr("README.txt", f"该日期 ({date_str}) 无符合条件的面试记录")

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def export_sessions_by_grade_zip(self, grade: str, days: int = 30, export_format: str = "both") -> bytes:
        """
        Export all sessions of a specific grade across multiple days as ZIP archive.

        Args:
            grade: Grade to filter (S, A, B, C)
            days: Number of days to look back
            export_format: "json", "html", or "both"

        Returns:
            ZIP file bytes
        """
        import io
        import zipfile
        from datetime import timedelta

        today = datetime.now().date()
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            count = 0

            for i in range(days):
                date = today - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                date_dir = self.base_dir / date_str

                if not date_dir.exists():
                    continue

                for session_file in date_dir.glob("*_session.json"):
                    try:
                        with open(session_file, "r", encoding="utf-8") as f:
                            session_data = json.load(f)

                        session_prefix = session_file.stem.replace("_session", "")
                        eval_file = date_dir / f"{session_prefix}_evaluation.json"

                        eval_data = None
                        if eval_file.exists():
                            try:
                                with open(eval_file, "r", encoding="utf-8") as ef:
                                    eval_data = json.load(ef)
                            except Exception:
                                pass

                        # Filter by grade
                        session_grade = eval_data.get("decision_tier") if eval_data else None
                        if session_grade != grade:
                            continue

                        # Get candidate name for filename
                        candidate_name = session_data.get("candidate_name", "Unknown")
                        safe_name = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '-', '_')).strip()
                        safe_name = safe_name[:30] if safe_name else "unknown"

                        # Create JSON content
                        json_content = json.dumps({
                            "session": session_data,
                            "evaluation": eval_data
                        }, ensure_ascii=False, indent=2, default=str)

                        # Add files to ZIP (include date in filename for cross-date export)
                        file_prefix = f"{date_str}_{grade}_{safe_name}_{session_prefix[:8]}"

                        if export_format in ("json", "both"):
                            zip_file.writestr(f"{file_prefix}.json", json_content.encode('utf-8'))

                        if export_format in ("html", "both"):
                            html_content = self._generate_single_session_html(
                                session_data, eval_data, date_str
                            )
                            zip_file.writestr(f"{file_prefix}.html", html_content.encode('utf-8'))

                        count += 1
                    except Exception:
                        continue

            if count == 0:
                zip_file.writestr("README.txt", f"最近 {days} 天内无 {grade} 级面试记录")

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_single_session_html(self, session_data: dict, eval_data: dict, date_str: str) -> str:
        """Generate HTML for a single session (used by ZIP export)"""
        candidate_name = session_data.get("candidate_name", "Unknown")
        candidate_email = session_data.get("candidate_email", "")
        candidate_phone = session_data.get("candidate_phone", "")
        candidate_wechat = session_data.get("candidate_wechat", "")
        turn_count = session_data.get("turn_count", 0)
        created_at = session_data.get("created_at", "")

        grade = eval_data.get("decision_tier", "") if eval_data else ""
        score = eval_data.get("total_score", "") if eval_data else ""
        summary = eval_data.get("summary", "") if eval_data else ""
        strengths = eval_data.get("key_strengths", []) if eval_data else []
        red_flags = eval_data.get("red_flags", []) if eval_data else []

        grade_class = f"grade-{grade}" if grade else ""
        strengths_html = "".join([f'<div class="list-item">{s}</div>' for s in strengths])
        red_flags_html = "".join([f'<div class="list-item">{r}</div>' for r in red_flags])

        chat_html = ""
        for msg in session_data.get("chat_history", []):
            role = msg.get("role", "")
            content = msg.get("content", "")
            role_label = "面试官" if role == "model" else "候选人"
            msg_class = "message-model" if role == "model" else "message-user"
            chat_html += f'''
            <div class="message {msg_class}">
                <div class="message-role">{role_label}</div>
                <div>{content}</div>
            </div>'''

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{candidate_name} - 面试记录</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #0D9488; border-bottom: 2px solid #0D9488; padding-bottom: 10px; }}
        .session {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .session-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .candidate-name {{ font-size: 1.25rem; font-weight: 600; color: #1E293B; }}
        .grade {{ padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.875rem; }}
        .grade-S {{ background: linear-gradient(135deg, #FCD34D, #F59E0B); color: #78350F; }}
        .grade-A {{ background: linear-gradient(135deg, #34D399, #10B981); color: #064E3B; }}
        .grade-B {{ background: linear-gradient(135deg, #60A5FA, #3B82F6); color: #1E3A8A; }}
        .grade-C {{ background: linear-gradient(135deg, #F87171, #EF4444); color: #7F1D1D; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 15px; }}
        .info-item {{ color: #64748B; font-size: 0.875rem; }}
        .info-label {{ font-weight: 500; color: #475569; }}
        .summary {{ background: #F8FAFC; padding: 15px; border-radius: 8px; margin-top: 15px; }}
        .chat-history {{ margin-top: 15px; border-top: 1px solid #E2E8F0; padding-top: 15px; }}
        .message {{ margin-bottom: 10px; padding: 10px; border-radius: 8px; }}
        .message-user {{ background: #E0F2FE; margin-left: 20px; }}
        .message-model {{ background: #ECFDF5; margin-right: 20px; }}
        .message-role {{ font-weight: 600; font-size: 0.75rem; color: #64748B; margin-bottom: 4px; }}
        .strengths {{ color: #059669; }}
        .red-flags {{ color: #DC2626; }}
        .list-item {{ margin: 4px 0; padding-left: 16px; position: relative; }}
        .list-item::before {{ content: "•"; position: absolute; left: 0; }}
    </style>
</head>
<body>
    <h1>{candidate_name} - 面试记录</h1>
    <p style="color: #64748B;">日期: {date_str} | 导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <div class="session">
        <div class="session-header">
            <span class="candidate-name">{candidate_name}</span>
            <span class="grade {grade_class}">{grade} {score}分</span>
        </div>
        <div class="info-grid">
            <div class="info-item"><span class="info-label">邮箱:</span> {candidate_email}</div>
            <div class="info-item"><span class="info-label">电话:</span> {candidate_phone}</div>
            <div class="info-item"><span class="info-label">微信:</span> {candidate_wechat}</div>
            <div class="info-item"><span class="info-label">面试时间:</span> {created_at}</div>
            <div class="info-item"><span class="info-label">对话轮次:</span> {turn_count} 轮</div>
        </div>
        {f'<div class="summary"><strong>评估总结:</strong> {summary}</div>' if summary else ''}
        <div style="display: flex; gap: 20px; margin-top: 15px;">
            <div class="strengths" style="flex: 1;"><strong>核心亮点:</strong>{strengths_html or '<div class="list-item">无</div>'}</div>
            <div class="red-flags" style="flex: 1;"><strong>关注点:</strong>{red_flags_html or '<div class="list-item">无</div>'}</div>
        </div>
        <div class="chat-history">
            <strong style="color: #0D9488;">完整对话记录</strong>
            {chat_html}
        </div>
    </div>
</body>
</html>"""


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
