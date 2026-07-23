# Response
`future.response.Response` is a mutable builder. Controllers return `self.response.…(...)` (same instance Future injected).

## Builders
```python
self.response.json(data, status=200)
self.response.html(html)
self.response.text("ok")
self.response.empty(status=204)
self.response.redirect("/x")
self.response.file(body_bytes, content_type="application/octet-stream")
self.response.image(body_bytes, content_type="image/png")
self.response.set_cookie("a", "b", max_age=3600, domain="example.com")
self.response.delete_cookie("a")
```

Each builder sets status, body, and headers, then returns `self` so you can chain cookies:

```python
return self.response.json({"ok": True}).set_cookie("sid", token, httponly=True)
```

## Errors
```python
from future.exceptions import HTTPException
raise HTTPException("Not Found", 404)
```

## Legacy wrappers
`JSONResponse`, `PlainTextResponse`, etc. still exist as thin subclasses. Prefer `self.response.json(...)` on the injected instance.

## Streaming
`StreamingResponse` is not implemented yet — see [Gaps](gaps.md).

WebSocket sessions use `WebSocketResponse` — see [WebSockets](websockets.md).
