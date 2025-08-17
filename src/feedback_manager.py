import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class FeedbackManager:
    """사용자 피드백 및 해석 이력 관리"""

    def __init__(self, feedback_file_path: Optional[str] = None):
        self.feedback_file_path = feedback_file_path
        self._data = {
            "interpretations": [],  # 모든 해석 시도 기록
            "feedbacks": []         # 모든 피드백 기록
        }
        self._feedback_id_counter = 1
        self._load_from_file()

    def _save_to_file(self):
        if self.feedback_file_path:
            with open(self.feedback_file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)

    def _load_from_file(self):
        if self.feedback_file_path and os.path.exists(self.feedback_file_path):
            with open(self.feedback_file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            if self._data.get("feedbacks"):
                self._feedback_id_counter = max([f["feedback_id"] for f in self._data["feedbacks"]]) + 1

    def record_interpretation_attempt(
        self,
        user_id: int,
        cards: List[str],
        persona: Dict[str, Any],
        context: Dict[str, Any],
        interpretations: List[str],
        method: str = "online"
    ) -> Dict[str, Any]:
        feedback_id = self._feedback_id_counter
        self._feedback_id_counter += 1

        attempt_record = {
            "feedback_id": feedback_id,
            "user_id": user_id,
            "cards": cards,
            "persona": persona,
            "context": context,
            "interpretations": interpretations,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }

        self._data["interpretations"].append(attempt_record)
        self._data["feedbacks"].append({
            "feedback_id": feedback_id,
            "user_id": user_id,
            "selected_interpretation_index": None,
            "user_correction": None,
            "timestamp": None
        })
        self._save_to_file()

        return {
            "status": "success",
            "feedback_id": feedback_id,
            "message": "Interpretation attempt recorded successfully."
        }

    def record_user_feedback(
        self,
        feedback_id: int,
        selected_interpretation_index: Optional[int] = None,
        user_correction: Optional[str] = None
    ) -> Dict[str, Any]:
        for fb in self._data["feedbacks"]:
            if fb["feedback_id"] == feedback_id:
                fb["selected_interpretation_index"] = selected_interpretation_index
                fb["user_correction"] = user_correction
                fb["timestamp"] = datetime.now().isoformat()
                self._save_to_file()
                return {"status": "success", "message": "Feedback recorded."}

        return {"status": "error", "message": f"Feedback ID {feedback_id} not found."}

    def get_user_interpretation_summary(self, user_id: int) -> Dict[str, Any]:
        user_interps = [i for i in self._data["interpretations"] if i["user_id"] == user_id]
        if not user_interps:
            return {"status": "success", "summary": "No history found.", "pattern_count": 0}

        summary_text = f"Total {len(user_interps)} attempts. Frequently used cards: "
        card_usage = {}
        for interp in user_interps:
            for card in interp["cards"]:
                card_usage[card] = card_usage.get(card, 0) + 1
        sorted_cards = sorted(card_usage.items(), key=lambda x: x[1], reverse=True)
        summary_text += ", ".join([f"{c}({cnt})" for c, cnt in sorted_cards[:5]])

        return {
            "status": "success",
            "summary": summary_text,
            "pattern_count": len(sorted_cards)
        }

    def get_card_interpretation_patterns(self, cards: List[str]) -> Dict[str, Any]:
        patterns = []
        scores = []
        for interp in self._data["interpretations"]:
            if set(cards).issubset(set(interp["cards"])):
                patterns.append(interp)
                scores.append(1.0)  # 간단하게 relevance score는 1.0 부여

        return {
            "status": "success",
            "patterns": patterns,
            "relevance_scores": scores
        }

    def get_feedback_statistics(self) -> Dict[str, Any]:
        total_attempts = len(self._data["interpretations"])
        completed_feedback = sum(1 for f in self._data["feedbacks"] if f["selected_interpretation_index"] is not None or f["user_correction"])
        completion_rate = (completed_feedback / total_attempts) if total_attempts else 0.0

        corrections = sum(1 for f in self._data["feedbacks"] if f["user_correction"])
        correction_rate = (corrections / total_attempts) if total_attempts else 0.0

        # 간단하게 accuracy는 해석 선택 여부로 계산
        average_accuracy = (completed_feedback - corrections) / total_attempts if total_attempts else 0.0

        return {
            "total_attempts": total_attempts,
            "completed_feedback": completed_feedback,
            "completion_rate": completion_rate,
            "average_accuracy": average_accuracy,
            "correction_rate": correction_rate
        }

    def get_user_feedback_history(self, user_id: int, limit: int = 20) -> Dict[str, Any]:
        user_feedbacks = [f for f in self._data["feedbacks"] if f["user_id"] == user_id]
        total_count = len(user_feedbacks)
        history = sorted(user_feedbacks, key=lambda x: x.get("timestamp") or "", reverse=True)[:limit]

        return {
            "status": "success",
            "history": history,
            "total_count": total_count
        }

    def delete_user_feedback(self, user_id: int) -> Dict[str, Any]:
        before_count = len(self._data["feedbacks"])
        self._data["feedbacks"] = [f for f in self._data["feedbacks"] if f["user_id"] != user_id]
        self._data["interpretations"] = [i for i in self._data["interpretations"] if i["user_id"] != user_id]
        after_count = len(self._data["feedbacks"])

        deleted_count = before_count - after_count
        self._save_to_file()
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} feedback(s) for user {user_id}."
        }
