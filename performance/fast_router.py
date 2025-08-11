"""
Fast Router for Future Framework
Optimized route matching with Cython support.
"""

from typing import Dict, List, Optional, Any
import re

# Try to import the Cython version first
try:
    from performance.fast_router_cy import FastRouterCython
    FastRouter = FastRouterCython
    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False


class FastRouter:
    """Fast router using trie-based matching."""
    
    def __init__(self):
        self.routes = {}
        self.static_routes = {}
        self.dynamic_routes = []
        self.param_names = {}
    
    def add_route(self, path: str, handler_data: dict) -> None:
        """Add a route to the fast router."""
        # Store parameter names for this route
        param_names = []
        for segment in path.split('/'):
            if segment.startswith(':'):
                param_names.append(segment[1:])
        
        self.param_names[path] = param_names
        
        # Separate static and dynamic routes for faster matching
        if ':' in path or '<' in path or '{' in path:
            # Dynamic route - compile regex
            pattern = self._compile_pattern(path)
            self.dynamic_routes.append({
                'pattern': pattern,
                'path': path,
                'handler_data': handler_data,
                'param_names': param_names
            })
        else:
            # Static route - direct lookup
            self.static_routes[path] = handler_data
    
    def _compile_pattern(self, path: str) -> re.Pattern:
        """Compile a route pattern to regex."""
        # Convert route parameters to regex
        pattern = path
        pattern = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', pattern)
        pattern = re.sub(r'<(\w+):(\w+)>', r'(?P<\2>[^/]+)', pattern)
        pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', pattern)
        pattern = f"^{pattern}$"
        return re.compile(pattern)
    
    def match(self, request_path: bytes) -> Optional[dict]:
        """Match a request path against the router."""
        path = request_path.decode('utf-8')
        
        # Try static routes first (fastest)
        if path in self.static_routes:
            return {
                'handler': self.static_routes[path]['handler'],
                'middleware': self.static_routes[path]['middleware'],
                'params': {}
            }
        
        # Try dynamic routes
        for route in self.dynamic_routes:
            match = route['pattern'].match(path)
            if match:
                params = match.groupdict()
                return {
                    'handler': route['handler_data']['handler'],
                    'middleware': route['handler_data']['middleware'],
                    'params': params
                }
        
        return None


class FastRouterFallback:
    """Fallback router for when fast router is not available."""
    
    def __init__(self):
        self.routes = {}
    
    def add_route(self, path: str, handler_data: dict) -> None:
        """Add a route to the fallback router."""
        self.routes[path] = handler_data
    
    def match(self, request_path: bytes) -> Optional[dict]:
        """Match a request path against the router."""
        path = request_path.decode('utf-8')
        if path in self.routes:
            return {
                'handler': self.routes[path]['handler'],
                'middleware': self.routes[path]['middleware'],
                'params': {}
            }
        return None


# Use Cython version if available, otherwise fallback
if not CYTHON_AVAILABLE:
    # If Cython version is not available, use the pure Python version
    pass 