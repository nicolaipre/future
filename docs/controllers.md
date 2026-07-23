# Controllers
Controllers get `request` / `response` from a base class. Routes are plain lists. No route decorators.

`future.controllers.Controller` injects them in `__init__`:

```python
from future.controllers import Controller
from future.response import Response

class StockController(Controller):
    async def get_stock(self, stock_id: str) -> Response:
        return self.response.json({"id": stock_id})
```

Do not add your own `__init__` unless you need extra deps — Future constructs `YourController(request, response)` per request.

## Example
```python
from future.controllers import Controller
from future.response import Response
from app.models.Stock import Stock

class StockController(Controller):
    async def get_stocks(self) -> Response:
        instrument_id = self.request.query.get("instrument_id")
        if instrument_id:
            stocks = Stock.where("instrument_id", instrument_id).get()
        else:
            stocks = Stock.all()
        return self.response.json([stock.to_dict() for stock in stocks], status=200)

    async def get_stock(self, stock_id: str) -> Response:
        stock = Stock.find(stock_id)
        if stock is None:
            return self.response.json({"error": "Not found"}, status=404)
        return self.response.json(stock.to_dict(), status=200)
```

Register **class method references**, not instances:

```python
from future.routing import Get

Get("/stocks", StockController.get_stocks, "stocks")
Get("/stocks/<str:stock_id>", StockController.get_stock, "stocks.show")
```

Path params become action kwargs. See [Routing](routing.md), [Request](request.md), [Response](response.md).
