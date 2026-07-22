# OpenAPI schema registry + route factory for docs UIs.


import re

from future.routing import Get
from future.settings import APP_DESCRIPTION, APP_NAME, APP_VERSION


_DEFAULT_UIS = ["swagger", "redoc", "scalar", "rapidoc"]
_DOC_PATH_ENDS = ("/openapi.json", "/swagger-config", "/docs", "/redoc", "/scalar", "/rapidoc")

_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
    },
    "paths": {},
}

_CONFIG = {
    "enabled": True,
    "uis": list(_DEFAULT_UIS),
    "auto_routes": False,
    "path_prefix": "",
    "redocly_license_key": "",  # paid Redocly Reference Docs (Try it); empty = OSS ReDoc
    "servers": None,  # list of {"url": "...", "description": "..."} or None → derive from APP_DOMAIN
    "security_schemes": None,  # OpenAPI components.securitySchemes map
    "security": None,  # global security requirements
    "models": [],  # model classes → components.schemas via Model.openapi_schema()
}


def get_openapi_config(config=None):
    if config and isinstance(config.get("OPENAPI"), dict):
        merged = dict(_CONFIG)
        merged.update(config["OPENAPI"])
        if "uis" not in config["OPENAPI"]:
            merged["uis"] = list(_DEFAULT_UIS)
        return merged
    return dict(_CONFIG)


def set_openapi_config(config):
    global _CONFIG
    if not config:
        return
    openapi = config.get("OPENAPI") if isinstance(config, dict) else None
    if not isinstance(openapi, dict):
        return
    _CONFIG = get_openapi_config(config)


def get_spec():
    return _SPEC


def path_prefix():
    return _CONFIG.get("path_prefix") or ""


def spec_path():
    return f"{path_prefix()}/openapi.json"


def is_docs_path(path):
    for ending in _DOC_PATH_ENDS:
        if path == ending or path.endswith(ending):
            return True
    return False


def rebuild_spec_from_routes(routes_by_domain, app_config=None):
    global _SPEC
    cfg = get_openapi_config(app_config)
    info_title = APP_NAME
    info_version = APP_VERSION
    info_description = APP_DESCRIPTION
    if app_config:
        info_title = app_config.get("APP_NAME", info_title)
        info_version = app_config.get("APP_VERSION", info_version)
        info_description = app_config.get("APP_DESCRIPTION", info_description)
    paths = {}
    schemas = {}
    for model in cfg.get("models") or []:
        schemas[model.__name__] = model().openapi_schema()
    if cfg.get("enabled", True):
        for route_map in routes_by_domain.values():
            for route_key, route_config in route_map.items():
                route = route_config.get("route")
                path = getattr(route, "path", None) or (route_key.split(" ", 1)[-1] if " " in str(route_key) else route_key)
                if is_docs_path(path):
                    continue
                operation_id = getattr(route, "name", None) or path
                handler = route_config.get("handler") or getattr(route, "endpoint", None)
                doc = ""
                if handler is not None:
                    doc = (getattr(handler, "__doc__", None) or "").strip()
                summary = None
                description = None
                if doc:
                    # FastAPI-style: first line = summary, remainder = description (Markdown OK)
                    lines = doc.split("\n", 1)
                    summary = lines[0].strip() or None
                    if len(lines) > 1:
                        description = "\n".join(line.rstrip() for line in lines[1].splitlines()).strip() or None
                        # Drop common leading indent from the body
                        if description:
                            body_lines = description.splitlines()
                            indents = [len(line) - len(line.lstrip()) for line in body_lines if line.strip()]
                            if indents:
                                pad = min(indents)
                                description = "\n".join(line[pad:] if len(line) >= pad else line for line in body_lines).strip()
                param_schemas = {}
                for match in re.finditer(r"/<(?:([^:>]+):)?([^>]+)>", path):
                    type_name = match.group(1) or "string"
                    param_name = match.group(2)
                    if type_name == "int":
                        param_schemas[param_name] = {"type": "integer"}
                    elif type_name == "float":
                        param_schemas[param_name] = {"type": "number"}
                    elif type_name == "uuid":
                        param_schemas[param_name] = {"type": "string", "format": "uuid"}
                    else:
                        param_schemas[param_name] = {"type": "string"}
                for match in re.finditer(r"/\{(?:([^:}]+):)?([^}]+)\}", path):
                    type_name = match.group(1) or "string"
                    param_name = match.group(2)
                    if type_name == "int":
                        param_schemas[param_name] = {"type": "integer"}
                    elif type_name == "float":
                        param_schemas[param_name] = {"type": "number"}
                    elif type_name == "uuid":
                        param_schemas[param_name] = {"type": "string", "format": "uuid"}
                    else:
                        param_schemas[param_name] = {"type": "string"}
                path = re.sub(r"/<(?:[^:>]+:)?([^>]+)>", r"/{\1}", path)
                path = re.sub(r"/\{(?:[^:}]+:)?([^}]+)\}", r"/{\1}", path)
                path = re.sub(r"/:([A-Za-z_][A-Za-z0-9_]*)", r"/{\1}", path)
                entry = paths.setdefault(path, {})
                for method in route_config.get("methods") or ["GET"]:
                    operation = {
                        "operationId": operation_id,
                        "responses": {"200": {"description": "OK"}},
                    }
                    if summary:
                        operation["summary"] = summary
                    if description:
                        operation["description"] = description
                    group_name = (route_config.get("group") or {}).get("name")
                    if group_name:
                        operation["tags"] = [group_name]
                    parameters = []
                    for param_name in getattr(route, "param_names", None) or []:
                        parameters.append({
                            "name": param_name,
                            "in": "path",
                            "required": True,
                            "schema": param_schemas.get(param_name) or {"type": "string"},
                        })
                    if parameters:
                        operation["parameters"] = parameters
                    if method.upper() in ("POST", "PUT", "PATCH"):
                        operation["requestBody"] = {
                            "required": False,
                            "content": {
                                "application/json": {"schema": {"type": "object"}},
                                "application/x-www-form-urlencoded": {"schema": {"type": "object"}},
                                "multipart/form-data": {"schema": {"type": "object"}},
                            },
                        }
                    entry[method.lower()] = operation
    servers = cfg.get("servers")
    if servers is None and app_config:
        domain = app_config.get("APP_DOMAIN") or ""
        scheme = "https"
        if domain:
            servers = [{"url": f"{scheme}://{domain}", "description": "Application"}]
    components = {}
    security_schemes = cfg.get("security_schemes")
    if security_schemes:
        components["securitySchemes"] = security_schemes
    if schemas:
        components["schemas"] = schemas
    _SPEC = {
        "openapi": "3.0.0",
        "info": {
            "title": info_title,
            "version": str(info_version),
            "description": info_description,
        },
        "paths": paths,
    }
    if servers:
        _SPEC["servers"] = servers
    if components:
        _SPEC["components"] = components
    if cfg.get("security"):
        _SPEC["security"] = cfg["security"]
    return _SPEC


def openapi_routes(uis=None, path_prefix=None, config=None):
    # Paths are root-relative (`/scalar`, …). Mount with RouteGroup(prefix=...); path_prefix only affects HTML spec URLs.
    from future.controllers import OpenAPIController
    global _CONFIG
    cfg = get_openapi_config(config)
    if not cfg.get("enabled", True):
        return []
    selected = uis if uis is not None else cfg.get("uis") or _DEFAULT_UIS
    prefix = path_prefix if path_prefix is not None else (cfg.get("path_prefix") or "")
    _CONFIG["path_prefix"] = prefix
    if uis is not None:
        _CONFIG["uis"] = list(selected)
    routes = [
        Get("/openapi.json", OpenAPIController.openapi, "openapi"),
    ]
    if "swagger" in selected:
        routes.append(Get("/swagger-config", OpenAPIController.swagger_config, "swagger-config"))
        routes.append(Get("/docs", OpenAPIController.swagger, "docs"))
    if "redoc" in selected:
        routes.append(Get("/redoc", OpenAPIController.redoc, "redoc"))
    if "scalar" in selected:
        routes.append(Get("/scalar", OpenAPIController.scalar, "scalar"))
    if "rapidoc" in selected:
        routes.append(Get("/rapidoc", OpenAPIController.rapidoc, "rapidoc"))
    return routes
