from sanic import Sanic
from sanic.response import text

app = Sanic("benchmark")

@app.get("/")
async def home(request):
    # Only respond if Host header is example.com
    #if request.host.split(':')[0] != "example.com":
    #    return text("Forbidden", status=403)
    return text("Hello, Sanic!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, workers=1, access_log=False)