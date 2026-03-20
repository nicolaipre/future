# TODO


## FIXME
- [ ] Automatic mapping for GET params work. Make it work for POST too.
    - [ ] Inject into scope.context ? or something else?
    - [ ] Make sure it works for ALL request types
- [ ] Look at Masonite routes + base Controller. It uses `__init__` which injects request and response so you can pass self, request: Request, response: Response to controller methods and avoid Python errors and staticmethod dogshitorators.
- [ ] Fix Future complaining about duplicate routes which really isnt duplicate routes since they use different HTTP methods for the same path:
```shell
  File "/home/ad.ialoc.in/n/Documents/git/datalake/.venv/lib/python3.13/site-packages/future/application.py", line 272, in _check_route_conflicts
    raise ValueError(f"Route conflict detected: {route.path} already exists in domain {domain}")
ValueError: Route conflict detected: /elasticsearch/ already exists in domain localhost
```
- [ ] Update the code to account for not only route.path, but route.path AND route.method (same as the MEGABUG?)
- [ ] Use httpx instead of requests. We need HTTP/2 support on everything. Alternatively use hypercorn for HTTP/2, although everything should be behind an instance of nginx. Uvicorn has HTTP/2 support on its roadmap but it is not implemented yet.
- [ ] Reconsider slicing :5000 (port) from the hostname check? Horrible to debug with it. Alternatively let debug=True slice it away? Or just debug by setting Host header and curl towards 127.0.0.1? Maybe the best way to do it actually...
- [ ] Check that both bracket and mustache syntax works in route definitions
- [ ] Ensure we verify that HTTP Response is a valid HTTP Response type. Python dicts currently throw this error:
```shell
  File "/home/ad.ialoc.in/n/Documents/git/datalake/.venv/lib/python3.13/site-packages/future/application.py", line 465, in __call__
    await self.handle_http_request(scope, receive, send)
  File "/home/ad.ialoc.in/n/Documents/git/datalake/.venv/lib/python3.13/site-packages/future/application.py", line 385, in handle_http_request
    await response(send)
          ~~~~~~~~^^^^^^
TypeError: 'dict' object is not callable
```
- [ ] Review requests.py body() and json() and decide what to use