from typing import Any, Callable, Optional, TypedDict
from future.middleware import Middleware
import re


class RegexConfig(TypedDict):
    paths: list[re.Pattern]

class RouteException(Exception):
    pass

class InvalidValuePatternName(RouteException):
    def __init__(self, pattern_name: str, matched_parameter: str):
        self.pattern_name = pattern_name
        self.matched_parameter = matched_parameter
        super().__init__(f"Invalid value pattern name: {pattern_name} in {matched_parameter}")

class RouteMatch:
    def __init__(self, route: 'Route', params: Optional[dict[str, str]]):
        self.route = route
        self.params = params

class Route:
    value_patterns = {
        "string": r"[^\/]+",
        "str": r"[^\/]+",
        "path": r".*",
        "int": r"\d+",
        "float": r"\d+(?:\.\d+)?",
        "uuid": r"[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}",
    }

    def __init__(
        self,
        methods: list[str],
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        self.methods = methods
        self.path = path
        self.endpoint = endpoint
        self.name = name
        self.strict_slashes = strict_slashes
        self.middlewares = middlewares or []
        self._compile_pattern()

    def _compile_pattern(self) -> None:        
        _route_all_rx = re.compile(b"\\*")
        _route_param_rx = re.compile(b"/:([^/]+)")
        
        _mustache_route_param_rx = re.compile(b"/{([^}]+)}")
        _angle_bracket_route_param_rx = re.compile(b"/<([^>]+)>")

        _named_group_rx = re.compile(b"\\?P<([^>]+)>")
        _escaped_chars = {
            b".",
            b"[",
            b"]",
            b"(",
            b")",
        }

        def _get_parameter_pattern_fragment(name: str, pattern: Optional[str] = None) -> bytes:
            if pattern is None:
                pattern = Route.value_patterns["string"]
            return rb"/(?P<" + name.encode() + rb">" + pattern.encode() + rb")"

        def _handle_rich_parameter(match: re.Match) -> bytes:
            matched_parameter = next(iter(match.groups()))
            assert isinstance(matched_parameter, bytes)

            if b":" in matched_parameter:
                raw_pattern_name, parameter_name = matched_parameter.split(b":")
                parameter_pattern_name = raw_pattern_name.decode()
                parameter_pattern = Route.value_patterns.get(parameter_pattern_name)
                
                if not parameter_pattern:
                    raise InvalidValuePatternName(parameter_pattern_name, matched_parameter.decode("utf8"))

                return _get_parameter_pattern_fragment(parameter_name.decode(), parameter_pattern)
            
            return _get_parameter_pattern_fragment(matched_parameter.decode())


        pattern = self.path.encode()
        for c in _escaped_chars:
            if c in pattern:
                pattern = pattern.replace(c, b"\\" + c)


        if b"*" in pattern:
            if pattern.count(b"*") > 1:
                raise RouteException("A route pattern cannot contain more than one star sign *.")
            if b"/*" in pattern:
                pattern = _route_all_rx.sub(rb"?(?P<tail>.*)", pattern)
            else:
                pattern = _route_all_rx.sub(rb"(?P<tail>.*)", pattern)


        if b"<" in pattern:
            pattern = _angle_bracket_route_param_rx.sub(_handle_rich_parameter, pattern)

        if b"{" in pattern:
            pattern = _mustache_route_param_rx.sub(_handle_rich_parameter, pattern)

        if b"/:" in pattern:
            pattern = _route_param_rx.sub(rb"/(?P<\1>[^\/]+)", pattern)


        param_names = []
        for p in _named_group_rx.finditer(pattern):
            param_name = p.group(1).decode()
            
            if param_name in param_names:
                raise ValueError(f"cannot have multiple parameters with name: {param_name}")
            
            param_names.append(param_name)


        if len(pattern) > 1 and not pattern.endswith(b"*"):
            pattern = pattern + b"/?"


        self._rx = re.compile(b"^" + pattern + b"$", re.IGNORECASE)
        self.param_names = param_names


    def match(self, request_path: bytes) -> Optional[RouteMatch]:        
        match = self._rx.match(request_path)
        if not match:
            return None
        
        lol = RouteMatch(self, match.groupdict() if self.param_names else None)
        return lol


class Get(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["GET"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Post(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["POST"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Put(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["PUT"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Head(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["HEAD"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Options(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["OPTIONS"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Patch(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["PATCH"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Delete(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["DELETE"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class RouteGroup:
    def __init__(
        self,
        routes: list[Route],
        name: str = "",
        prefix: str = "",
        subdomain: str = "",
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        self.name = name
        self.prefix = prefix
        self.routes = routes
        self.subdomain = subdomain
        self.middlewares = middlewares or []

class EndpointConfig(TypedDict):
    middleware_before: list[Middleware]
    middleware_after: list[Middleware]
    route: Route
