# JSON Reponse til future:



class JSONResponse(Response):
    def __init__(self, data, status: int = 200, headers=None):
        json_body = json.dumps(data).encode("utf-8")

        default_headers = {
            "Content-Type": "application/json",
        }
        
        if headers:
            default_headers.update(headers)

        super().__init__(body=json_body, status=status, headers=default_headers)

