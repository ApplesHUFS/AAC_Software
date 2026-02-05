"""Feedback domain module"""

from app.domain.feedback.entity import Feedback, FeedbackRequest
from app.domain.feedback.service import FeedbackService

__all__ = ["Feedback", "FeedbackRequest", "FeedbackService"]
