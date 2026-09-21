"""Benchmark tests.

This file exists so `benchmark.tests` is an importable package. Without it,
plain `python3 -m unittest discover` from the repository root walks into the
`benchmark` package, skips this directory because it cannot be imported, and
reports success having run nothing.
"""
