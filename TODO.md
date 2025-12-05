# FIXME

Automatic mapping for GET params work

- Make it work for POST too
- Inject into scope.context ? or something else?
- Make sure it works for ALL request types


Se på Masonite routes + base Controller. Der har vi __init__ som injecter request og response, så man kan passe både self og request: Request til controller methods og slippe unna python errors og staticmethods


# ---

  File "/home/ad.ialoc.in/n/Documents/git/datalake/.venv/lib/python3.13/site-packages/future/application.py", line 272, in _check_route_conflicts
    raise ValueError(f"Route conflict detected: {route.path} already exists in domain {domain}")
ValueError: Route conflict detected: /elasticsearch/ already exists in domain localhost


Klager over duplicate routes som egentlig ikke er duplicate routes. Det er routes som har samme path, men forskjellig HTTP Method.

FIX1: Oppdater koden til å accounte for ikke kun route.path, men route.path + HTTP Method

FIX2: Bruk httpx instedefor requests. Vi trenger HTTP/2 på alt. Alternativt bruk hypercorn for HTTP/2, men alt skal likevel stå bak nginx.

FIX3: Vurder på nytt om vi skal slice :5000 (port) fra hostname checken. Dritt å debugge med den. Alternativt la debug=True droppe den.

FIX4: Sjekk at både bracket og mustache syntax funker i route defs

FIX5: ensure we verify that HTTP Response is a valid HTTP Response type. python dicts throw this error:
  File "/home/ad.ialoc.in/n/Documents/git/datalake/.venv/lib/python3.13/site-packages/future/application.py", line 465, in __call__
    await self.handle_http_request(scope, receive, send)
  File "/home/ad.ialoc.in/n/Documents/git/datalake/.venv/lib/python3.13/site-packages/future/application.py", line 385, in handle_http_request
    await response(send)
          ~~~~~~~~^^^^^^
TypeError: 'dict' object is not callable

