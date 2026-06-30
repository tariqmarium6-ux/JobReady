from datetime import datetime
import json
from database_interface import DatabaseInterface

class FirestoreProvider(DatabaseInterface):
    def __init__(self):
        try:
            from google.cloud import firestore
            self.db = firestore.Client()
        except Exception as e:
            print(f"[ERROR]: Failed to initialize Firestore Client: {e}")
            self.db = None

    def _is_active(self):
        return self.db is not None

    def get_user_profile(self, google_id: str) -> dict:
        if not self._is_active():
            return {}
        try:
            doc_ref = self.db.collection("users").document(google_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"[Firestore Error] get_user_profile: {e}")
        return {}

    def save_user_profile(self, profile_data: dict) -> bool:
        if not self._is_active():
            return False
        try:
            google_id = profile_data.get("google_id")
            doc_ref = self.db.collection("users").document(google_id)
            data = {
                "google_id": google_id,
                "email": profile_data.get("email"),
                "name": profile_data.get("name"),
                "picture_url": profile_data.get("picture_url"),
                "created_at": profile_data.get("created_at", datetime.utcnow().isoformat()),
                "streak_count": profile_data.get("streak_count", 0),
                "last_active_date": profile_data.get("last_active_date"),
                "study_pace": profile_data.get("study_pace", 15),
                "password_hash": profile_data.get("password_hash")
            }
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"[Firestore Error] save_user_profile: {e}")
            return False

    def get_progress(self, google_id: str, role_name: str) -> dict:
        fallback = {
            "google_id": google_id,
            "role_name": role_name,
            "completed_weeks": [],
            "completed_projects": [],
            "completed_materials": [],
            "bookmarks": {},
            "study_hours": 0.0
        }
        if not self._is_active():
            return fallback
        try:
            doc_id = f"{google_id}_{role_name.replace('/', '_')}"
            doc_ref = self.db.collection("progress").document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                # Ensure correct types
                if "completed_weeks" not in data: data["completed_weeks"] = []
                if "completed_projects" not in data: data["completed_projects"] = []
                if "completed_materials" not in data: data["completed_materials"] = []
                if "bookmarks" not in data: data["bookmarks"] = {}
                return data
        except Exception as e:
            print(f"[Firestore Error] get_progress: {e}")
        return fallback

    def save_progress(self, google_id: str, role_name: str, progress_data: dict) -> bool:
        if not self._is_active():
            return False
        try:
            doc_id = f"{google_id}_{role_name.replace('/', '_')}"
            doc_ref = self.db.collection("progress").document(doc_id)
            data = {
                "google_id": google_id,
                "role_name": role_name,
                "completed_weeks": list(progress_data.get("completed_weeks", [])),
                "completed_projects": list(progress_data.get("completed_projects", [])),
                "completed_materials": list(progress_data.get("completed_materials", [])),
                "bookmarks": dict(progress_data.get("bookmarks", {})),
                "study_hours": float(progress_data.get("study_hours", 0.0))
            }
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"[Firestore Error] save_progress: {e}")
            return False

    def get_quiz_record(self, google_id: str, role_name: str, week_num: int) -> dict:
        fallback = {
            "google_id": google_id,
            "role_name": role_name,
            "week_num": week_num,
            "attempt_count": 0,
            "best_score": 0,
            "last_attempt_date": None
        }
        if not self._is_active():
            return fallback
        try:
            doc_id = f"{google_id}_{role_name.replace('/', '_')}_{week_num}"
            doc_ref = self.db.collection("quizzes").document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"[Firestore Error] get_quiz_record: {e}")
        return fallback

    def save_quiz_record(self, google_id: str, role_name: str, week_num: int, record_data: dict) -> bool:
        if not self._is_active():
            return False
        try:
            doc_id = f"{google_id}_{role_name.replace('/', '_')}_{week_num}"
            doc_ref = self.db.collection("quizzes").document(doc_id)
            data = {
                "google_id": google_id,
                "role_name": role_name,
                "week_num": int(week_num),
                "attempt_count": int(record_data.get("attempt_count", 0)),
                "best_score": int(record_data.get("best_score", 0)),
                "last_attempt_date": record_data.get("last_attempt_date")
            }
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"[Firestore Error] save_quiz_record: {e}")
            return False

    def get_cached_quiz(self, role_name: str, week_num: int, prompt_hash: str) -> dict:
        if not self._is_active():
            return {}
        try:
            doc_id = f"{role_name.replace('/', '_')}_{week_num}_{prompt_hash}"
            doc_ref = self.db.collection("quiz_questions").document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                res_data = doc.to_dict()
                if "questions_json" in res_data:
                    return json.loads(res_data["questions_json"])
        except Exception as e:
            print(f"[Firestore Error] get_cached_quiz: {e}")
        return {}

    def save_cached_quiz(self, role_name: str, week_num: int, prompt_hash: str, quiz_data: dict) -> bool:
        if not self._is_active():
            return False
        try:
            doc_id = f"{role_name.replace('/', '_')}_{week_num}_{prompt_hash}"
            doc_ref = self.db.collection("quiz_questions").document(doc_id)
            data = {
                "role_name": role_name,
                "week_num": int(week_num),
                "prompt_hash": prompt_hash,
                "questions_json": json.dumps(quiz_data),
                "created_at": datetime.utcnow().isoformat()
            }
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"[Firestore Error] save_cached_quiz: {e}")
            return False

    def get_user_badges(self, google_id: str) -> list:
        if not self._is_active():
            return []
        try:
            badges_ref = self.db.collection("badges")
            query = badges_ref.where("google_id", "==", google_id)
            docs = query.stream()
            return [doc.to_dict().get("badge_name") for doc in docs if doc.to_dict().get("badge_name")]
        except Exception as e:
            print(f"[Firestore Error] get_user_badges: {e}")
        return []

    def add_user_badge(self, google_id: str, badge_name: str) -> bool:
        if not self._is_active():
            return False
        try:
            doc_id = f"{google_id}_{badge_name.replace(' ', '_')}"
            doc_ref = self.db.collection("badges").document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                return False  # Already exists
            data = {
                "google_id": google_id,
                "badge_name": badge_name,
                "awarded_at": datetime.utcnow().isoformat()
            }
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"[Firestore Error] add_user_badge: {e}")
            return False

    def get_user_by_email(self, email: str) -> dict:
        if not self._is_active():
            return {}
        try:
            users_ref = self.db.collection("users")
            query = users_ref.where("email", "==", email).limit(1)
            docs = list(query.stream())
            if docs:
                return docs[0].to_dict()
        except Exception as e:
            print(f"[Firestore Error] get_user_by_email: {e}")
        return {}

    def create_email_user(self, email: str, password_hash: str, name: str, picture_url: str) -> bool:
        if not self._is_active():
            return False
        import hashlib
        try:
            google_id = f"email_{hashlib.md5(email.encode('utf-8')).hexdigest()}"
            doc_ref = self.db.collection("users").document(google_id)
            doc = doc_ref.get()
            if doc.exists:
                return False
            data = {
                "google_id": google_id,
                "email": email,
                "name": name,
                "picture_url": picture_url,
                "created_at": datetime.utcnow().isoformat(),
                "streak_count": 1,
                "last_active_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "study_pace": 15,
                "password_hash": password_hash
            }
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"[Firestore Error] create_email_user: {e}")
            return False

