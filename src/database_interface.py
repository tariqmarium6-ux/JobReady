from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def get_user_profile(self, google_id: str) -> dict:
        """Retrieve user profile metadata by Google ID."""
        pass

    @abstractmethod
    def save_user_profile(self, profile_data: dict) -> bool:
        """Create or update user profile details."""
        pass

    @abstractmethod
    def get_progress(self, google_id: str, role_name: str) -> dict:
        """Retrieve current course progression data."""
        pass

    @abstractmethod
    def save_progress(self, google_id: str, role_name: str, progress_data: dict) -> bool:
        """Update course completion, study hours, and bookmarks."""
        pass

    @abstractmethod
    def get_quiz_record(self, google_id: str, role_name: str, week_num: int) -> dict:
        """Get user attempt counts and best scores for a week's quiz."""
        pass

    @abstractmethod
    def save_quiz_record(self, google_id: str, role_name: str, week_num: int, record_data: dict) -> bool:
        """Log quiz attempts, score achievements, and lock status."""
        pass

    @abstractmethod
    def get_cached_quiz(self, role_name: str, week_num: int, prompt_hash: str) -> dict:
        """Fetch cached versioned quiz questions if they match prompt hash."""
        pass

    @abstractmethod
    def save_cached_quiz(self, role_name: str, week_num: int, prompt_hash: str, quiz_data: dict) -> bool:
        """Cache generated quiz questions."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> dict:
        """Retrieve user profile metadata by email address."""
        pass

    @abstractmethod
    def create_email_user(self, email: str, password_hash: str, name: str, picture_url: str) -> bool:
        """Register a new user account with email and password hash."""
        pass

    @abstractmethod
    def get_user_badges(self, google_id: str) -> list:
        """Retrieve all badges earned by a user."""
        pass

    @abstractmethod
    def add_user_badge(self, google_id: str, badge_name: str) -> bool:
        """Award a new collectible badge to a user."""
        pass
