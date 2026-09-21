"""Errors that name the fixture row responsible for them."""

from __future__ import annotations


class FixtureError(ValueError):
    """A scenario, candidate, or tool call the evaluator cannot interpret.

    Raised instead of a bare ``KeyError`` or ``TypeError`` so the message says
    which scenario and which candidate the evaluator was looking at. Lab 1.4
    asks students to author new scenarios; the first thing they will do is get
    one wrong.
    """
