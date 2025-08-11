"""
Performance optimizations for the Future framework.

This package contains high-performance implementations including:
- Fast Router (pure Python)
- Cython Fast Router (C bindings)
- Optimized Application
- Performance testing examples
"""

from .optimized_application import OptimizedFuture
from .fast_router import FastRouter, FastRouterFallback

__all__ = [
    "OptimizedFuture",
    "FastRouter", 
    "FastRouterFallback"
]