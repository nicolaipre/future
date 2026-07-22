from future.controllers.base import Controller
from future.graphql.schema import queries, schema
from future.response import Response


class GraphQLController(Controller):
    async def query(self) -> Response:
        query = queries["GetEverything"]
        result = await schema.execute(query)
        if result.errors:
            return self.response.json({"errors": [str(error) for error in result.errors]}, status=400)
        return self.response.json(result.data)
