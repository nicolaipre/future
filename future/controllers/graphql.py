from future.controllers.base import Controller
from future.graphql.schema import schema as demo_schema
from future.response import Response


class GraphQLController(Controller):
    async def query(self) -> Response:
        body = await self.request.json()
        if not isinstance(body, dict):
            return self.response.json({"errors": ["JSON body required"]}, status=400)
        query = body.get("query")
        if not query or not isinstance(query, str):
            return self.response.json({"errors": ["query is required"]}, status=400)
        variables = body.get("variables")
        operation_name = body.get("operationName")
        app = self.request.scope.get("app")
        schema = (app.config.get("GRAPHQL_SCHEMA") if app and app.config else None) or demo_schema
        result = await schema.execute(query, variable_values=variables, operation_name=operation_name)
        payload = {"data": result.data}
        if result.errors:
            payload["errors"] = [str(error) for error in result.errors]
            return self.response.json(payload, status=400)
        return self.response.json(payload)
