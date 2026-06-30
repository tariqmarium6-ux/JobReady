import sqlite3
import json
import os
from datetime import datetime
from database_interface import DatabaseInterface

DB_PATH = os.path.join("database", "user_profiles.db")

class SQLiteProvider(DatabaseInterface):
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # User profile metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                google_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                picture_url TEXT,
                created_at TEXT NOT NULL,
                streak_count INTEGER DEFAULT 0,
                last_active_date TEXT,
                study_pace INTEGER DEFAULT 15
            )
        """)
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        except sqlite3.OperationalError:
            pass
        
        self.conn.commit()
        
        # Course progress
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                google_id TEXT,
                role_name TEXT,
                completed_weeks TEXT DEFAULT '[]',
                completed_projects TEXT DEFAULT '[]',
                completed_materials TEXT DEFAULT '[]',
                bookmarks TEXT DEFAULT '{}',
                study_hours REAL DEFAULT 0.0,
                PRIMARY KEY (google_id, role_name)
            )
        """)
        
        # Quiz attempts and scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                google_id TEXT,
                role_name TEXT,
                week_num INTEGER,
                attempt_count INTEGER DEFAULT 0,
                best_score INTEGER DEFAULT 0,
                last_attempt_date TEXT,
                PRIMARY KEY (google_id, role_name, week_num)
            )
        """)
        
        # Quiz questions cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                role_name TEXT,
                week_num INTEGER,
                prompt_hash TEXT,
                questions_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (role_name, week_num, prompt_hash)
            )
        """)
        
        # Earned badges
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS badges (
                google_id TEXT,
                badge_name TEXT,
                awarded_at TEXT NOT NULL,
                PRIMARY KEY (google_id, badge_name)
            )
        """)
        
        self.conn.commit()

    def get_user_profile(self, google_id: str) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {}

    def save_user_profile(self, profile_data: dict) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO users (google_id, email, name, picture_url, created_at, streak_count, last_active_date, study_pace)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_data.get("google_id"),
            profile_data.get("email"),
            profile_data.get("name"),
            profile_data.get("picture_url"),
            profile_data.get("created_at", datetime.utcnow().isoformat()),
            profile_data.get("streak_count", 0),
            profile_data.get("last_active_date"),
            profile_data.get("study_pace", 15)
        ))
        self.conn.commit()
        return True

    def get_progress(self, google_id: str, role_name: str) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM progress WHERE google_id = ? AND role_name = ?", (google_id, role_name))
        row = cursor.fetchone()
        if row:
            res = dict(row)
            # Parse JSON strings
            res["completed_weeks"] = json.loads(res.get("completed_weeks", "[]"))
            res["completed_projects"] = json.loads(res.get("completed_projects", "[]"))
            res["completed_materials"] = json.loads(res.get("completed_materials", "[]"))
            res["bookmarks"] = json.loads(res.get("bookmarks", "{}"))
            return res
        return {
            "google_id": google_id,
            "role_name": role_name,
            "completed_weeks": [],
            "completed_projects": [],
            "completed_materials": [],
            "bookmarks": {},
            "study_hours": 0.0
        }

    def save_progress(self, google_id: str, role_name: str, progress_data: dict) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO progress (google_id, role_name, completed_weeks, completed_projects, completed_materials, bookmarks, study_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            google_id,
            role_name,
            json.dumps(progress_data.get("completed_weeks", [])),
            json.dumps(progress_data.get("completed_projects", [])),
            json.dumps(progress_data.get("completed_materials", [])),
            json.dumps(progress_data.get("bookmarks", {})),
            progress_data.get("study_hours", 0.0)
        ))
        self.conn.commit()
        return True

    def get_quiz_record(self, google_id: str, role_name: str, week_num: int) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE google_id = ? AND role_name = ? AND week_num = ?", (google_id, role_name, week_num))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {
            "google_id": google_id,
            "role_name": role_name,
            "week_num": week_num,
            "attempt_count": 0,
            "best_score": 0,
            "last_attempt_date": None
        }

    def save_quiz_record(self, google_id: str, role_name: str, week_num: int, record_data: dict) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO quizzes (google_id, role_name, week_num, attempt_count, best_score, last_attempt_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            google_id,
            role_name,
            week_num,
            record_data.get("attempt_count", 0),
            record_data.get("best_score", 0),
            record_data.get("last_attempt_date")
        ))
        self.conn.commit()
        return True

    def get_cached_quiz(self, role_name: str, week_num: int, prompt_hash: str) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT questions_json FROM quiz_questions 
            WHERE role_name = ? AND week_num = ? AND prompt_hash = ?
        """, (role_name, week_num, prompt_hash))
        row = cursor.fetchone()
        if row:
            return json.loads(row["questions_json"])
        return {}

    def save_cached_quiz(self, role_name: str, week_num: int, prompt_hash: str, quiz_data: dict) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO quiz_questions (role_name, week_num, prompt_hash, questions_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            role_name,
            week_num,
            prompt_hash,
            json.dumps(quiz_data),
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()
        return True

    def get_user_badges(self, google_id: str) -> list:
        cursor = self.conn.cursor()
        cursor.execute("SELECT badge_name FROM badges WHERE google_id = ?", (google_id,))
        rows = cursor.fetchall()
        return [row["badge_name"] for row in rows]

    def add_user_badge(self, google_id: str, badge_name: str) -> bool:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO badges (google_id, badge_name, awarded_at)
                VALUES (?, ?, ?)
            """, (google_id, badge_name, datetime.utcnow().isoformat()))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Badge already earned
            return False

    def get_user_by_email(self, email: str) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {}

    def create_email_user(self, email: str, password_hash: str, name: str, picture_url: str) -> bool:
        import hashlib
        cursor = self.conn.cursor()
        google_id = f"email_{hashlib.md5(email.encode('utf-8')).hexdigest()}"
        try:
            cursor.execute("""
                INSERT INTO users (google_id, email, name, picture_url, created_at, streak_count, last_active_date, study_pace, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                google_id,
                email,
                name,
                picture_url,
                datetime.utcnow().isoformat(),
                1,
                datetime.utcnow().strftime("%Y-%m-%d"),
                15,
                password_hash
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
