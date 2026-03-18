"""Lightweight workflow scaffolding used for local development and smoke tests.

This file provides very small stand-ins for Workflow, Context and step so
example workflow modules (like `rag_agent.py`) can be imported without
pulling the full external framework during editing.

These implementations are intentionally minimal and **not** full-featured.
Replace them with your real implementations when ready.
"""
from types import SimpleNamespace
from typing import Any, Callable
import asyncio


class Store:
	def __init__(self):
		self._data = {}

	async def set(self, k: str, v: Any):
		self._data[k] = v

	async def get(self, k: str, default=None):
		return self._data.get(k, default)


class Context:
	def __init__(self):
		self.store = Store()

	# minimal event helpers used by example workflows; they are no-ops for smoke tests
	def write_event_to_stream(self, ev: Any):
		return None

	def send_event(self, ev: Any):
		return None

	def collect_events(self, ev: Any, types: list):
		return None


def step(fn: Callable):
	"""Small marker decorator for step functions. Returns the function unchanged.

	Replace with the real decorator from your workflow framework.
	"""

	return fn


class Workflow:
	def __init__(self, timeout: int | None = None):
		self.timeout = timeout


__all__ = ["Workflow", "Context", "step", "Store"]

