"""Shine v4 — AI-powered moneyline parlay engine."""

__version__ = "0.4.0"

from .engine.builder import ShineEngine
from .models import Leg, Parlay, Event, Tier

__all__ = ["ShineEngine", "Leg", "Parlay", "Event", "Tier"]
