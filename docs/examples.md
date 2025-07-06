# Examples

This page contains complete, working examples of Future framework applications, matching the explicit, declarative style of example.py.

## Basic API Server

```python
from future.application import Future
from future.controllers import WelcomeController, DebugController
from future.routing import Get

routes = [
    Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
    Get(path="/users/<int:user_id>", endpoint=DebugController.args, name="getUserInfo"),
]

app = Future()
app.add_routes(routes=routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## API Server with Route Groups and Middleware

```python
from future.application import Future
from future.controllers import WelcomeController, DebugController
from future.middleware import TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import Get, RouteGroup

api_routes = RouteGroup(
    name="API",
    prefix="/api",
    middlewares=[TestMiddlewareRequest, TestMiddlewareResponse],
    routes=[
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
        Get(path="/users/<int:user_id>", endpoint=DebugController.args, name="getUserInfo"),
    ],
)

routes = [api_routes]

app = Future()
app.add_routes(routes=routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## WebSocket Example

```python
from future.application import Future
from future.controllers import WebSocketController
from future.routing import WebSocket, RouteGroup

ws_routes = RouteGroup(
    name="websockets",
    subdomain="api",
    routes=[
        WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="websocket_endpoint"),
    ],
)

routes = [ws_routes]

app = Future()
app.add_routes(routes=routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## Lifespan, Startup, Shutdown, and Cron Tasks

```python
from future.application import Future
from future.lifespan import Lifespan
from future.scheduler import Task, Unit, check_dns, check_ssh_banner, check_system_uptime, daily_backup
from datetime import datetime, timedelta

startup_tasks = [
    Task("init_database", func=None),
    Task("load_config", func=None),
    Task("start_metrics", func=None),
]

shutdown_tasks = [
    Task("save_metrics", func=None),
    Task("close_connections", func=None),
]

cronjobs = [
    Task("dns_check", interval=5, unit=Unit.MINUTES, func=check_dns, args=("example.com",)),
    Task("ssh_banner_check", interval=10, unit=Unit.MINUTES, func=check_ssh_banner, args=("localhost", 22)),
    Task("system_uptime", interval=1, unit=Unit.HOURS, func=check_system_uptime),
    Task(
        "daily_backup",
        interval=1,
        unit=Unit.DAYS,
        start_time=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1),
        func=daily_backup,
    ),
]

lifespan = Lifespan(startup_tasks, shutdown_tasks, cronjobs)

app = Future(lifespan=lifespan)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## Full Example with Config

```python
from future.application import Future
from future.controllers import WelcomeController
from future.routing import Get
from future.settings import APP_NAME, APP_DOMAIN, APP_DEBUG, APP_LOG_LEVEL

routes = [
    Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
]

config = {
    "APP_NAME": APP_NAME,
    "APP_DOMAIN": APP_DOMAIN,
    "APP_DEBUG": APP_DEBUG,
    "APP_LOG_LEVEL": APP_LOG_LEVEL,
}

app = Future(config=config)
app.add_routes(routes=routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## Chat Application with WebSocket

A real-time chat application using WebSockets:

```python
from future import Future, Response, WebSocketRoute, WebSocketResponse
from future import Middleware, Request
import json

# Middleware for CORS
class CORSMiddleware(Middleware):
    def intercept(self, request: Request) -> Response | None:
        if request.method == "OPTIONS":
            response = Response("", status_code=200)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            return response
        return None

# WebSocket chat handler
class ChatWebSocket(WebSocketRoute):
    clients = []
    
    def handle(self, websocket: WebSocketResponse):
        self.clients.append(websocket)
        try:
            # Send welcome message
            websocket.send(json.dumps({
                "type": "system",
                "message": "Welcome to the chat!"
            }))
            
            # Broadcast user joined
            self.broadcast({
                "type": "system",
                "message": "A new user joined the chat"
            }, exclude=websocket)
            
            # Handle incoming messages
            while True:
                message = websocket.receive()
                if message is None:
                    break
                
                try:
                    data = json.loads(message)
                    if data.get("type") == "message":
                        # Broadcast message to all clients
                        self.broadcast({
                            "type": "message",
                            "user": data.get("user", "Anonymous"),
                            "message": data["message"]
                        })
                except json.JSONDecodeError:
                    websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))
        finally:
            self.clients.remove(websocket)
            # Broadcast user left
            self.broadcast({
                "type": "system",
                "message": "A user left the chat"
            })
    
    def broadcast(self, message, exclude=None):
        for client in self.clients:
            if client != exclude:
                client.send(json.dumps(message))

# Create application
app = Future()
app.add_middleware(CORSMiddleware)
app.add_websocket_route("/ws/chat", ChatWebSocket)

@app.route("/")
def home():
    return Response("""
    <!DOCTYPE html>
    <html>
    <head><title>Chat App</title></head>
    <body>
        <h1>Chat Application</h1>
        <div id="messages"></div>
        <input type="text" id="user" placeholder="Your name">
        <input type="text" id="message" placeholder="Message">
        <button onclick="sendMessage()">Send</button>
        
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws/chat');
            const messages = document.getElementById('messages');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const div = document.createElement('div');
                div.textContent = `${data.type}: ${data.message}`;
                messages.appendChild(div);
            };
            
            function sendMessage() {
                const user = document.getElementById('user').value || 'Anonymous';
                const message = document.getElementById('message').value;
                if (message) {
                    ws.send(JSON.stringify({
                        type: 'message',
                        user: user,
                        message: message
                    }));
                    document.getElementById('message').value = '';
                }
            }
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run()
```

## GraphQL API

A GraphQL API with user and post management:

```python
from future import Future, Response, GraphQLController
import strawberry
from typing import List, Optional

# GraphQL Types
@strawberry.type
class User:
    id: int
    name: str
    email: str
    posts: List['Post']

@strawberry.type
class Post:
    id: int
    title: str
    content: str
    author: User

# Mock data
users_data = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

posts_data = [
    {"id": 1, "title": "First Post", "content": "Hello World", "author_id": 1},
    {"id": 2, "title": "Second Post", "content": "Another post", "author_id": 2},
    {"id": 3, "title": "Third Post", "content": "Yet another", "author_id": 1}
]

# GraphQL Queries
@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        user_data = next((u for u in users_data if u["id"] == id), None)
        if user_data:
            return User(
                id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
                posts=[]
            )
        return None
    
    @strawberry.field
    def users(self) -> List[User]:
        return [
            User(
                id=user["id"],
                name=user["name"],
                email=user["email"],
                posts=[]
            )
            for user in users_data
        ]
    
    @strawberry.field
    def post(self, id: int) -> Optional[Post]:
        post_data = next((p for p in posts_data if p["id"] == id), None)
        if post_data:
            author_data = next(u for u in users_data if u["id"] == post_data["author_id"])
            return Post(
                id=post_data["id"],
                title=post_data["title"],
                content=post_data["content"],
                author=User(
                    id=author_data["id"],
                    name=author_data["name"],
                    email=author_data["email"],
                    posts=[]
                )
            )
        return None
    
    @strawberry.field
    def posts(self) -> List[Post]:
        return [
            Post(
                id=post["id"],
                title=post["title"],
                content=post["content"],
                author=User(
                    id=next(u for u in users_data if u["id"] == post["author_id"])["id"],
                    name=next(u for u in users_data if u["id"] == post["author_id"])["name"],
                    email=next(u for u in users_data if u["id"] == post["author_id"])["email"],
                    posts=[]
                )
            )
            for post in posts_data
        ]

# GraphQL Mutations
@strawberry.type
class Mutation:
    @strawberry.field
    def create_user(self, name: str, email: str) -> User:
        new_user = {
            "id": len(users_data) + 1,
            "name": name,
            "email": email
        }
        users_data.append(new_user)
        return User(
            id=new_user["id"],
            name=new_user["name"],
            email=new_user["email"],
            posts=[]
        )
    
    @strawberry.field
    def create_post(self, title: str, content: str, author_id: int) -> Post:
        new_post = {
            "id": len(posts_data) + 1,
            "title": title,
            "content": content,
            "author_id": author_id
        }
        posts_data.append(new_post)
        author_data = next(u for u in users_data if u["id"] == author_id)
        return Post(
            id=new_post["id"],
            title=new_post["title"],
            content=new_post["content"],
            author=User(
                id=author_data["id"],
                name=author_data["name"],
                email=author_data["email"],
                posts=[]
            )
        )

# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create application
app = Future()
app.add_graphql_route("/graphql", GraphQLController(schema))

@app.route("/")
def home():
    return Response("""
    <!DOCTYPE html>
    <html>
    <head><title>GraphQL API</title></head>
    <body>
        <h1>GraphQL API</h1>
        <p>Visit <a href="/graphql">/graphql</a> for the GraphQL playground</p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run()
```

## Scheduled Task Manager

An application with scheduled background tasks:

```python
from future import Future, Response, Scheduler
import time
import json

# Task scheduler
class TaskScheduler(Scheduler):
    def setup_schedules(self):
        return [
            (60, self.minute_task),      # Every minute
            (300, self.five_minute_task), # Every 5 minutes
            (3600, self.hourly_task),    # Every hour
            (86400, self.daily_task),    # Every day
        ]
    
    def minute_task(self):
        print(f"[{time.strftime('%H:%M:%S')}] Minute task executed")
        self.log_task("minute")
    
    def five_minute_task(self):
        print(f"[{time.strftime('%H:%M:%S')}] Five minute task executed")
        self.log_task("five_minute")
    
    def hourly_task(self):
        print(f"[{time.strftime('%H:%M:%S')}] Hourly task executed")
        self.log_task("hourly")
    
    def daily_task(self):
        print(f"[{time.strftime('%H:%M:%S')}] Daily task executed")
        self.log_task("daily")
    
    def log_task(self, task_type: str):
        try:
            with open("task_log.json", "r") as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = {}
        
        if task_type not in logs:
            logs[task_type] = []
        
        logs[task_type].append({
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        with open("task_log.json", "w") as f:
            json.dump(logs, f, indent=2)

# Create application
app = Future()
app.set_scheduler(TaskScheduler())

@app.route("/")
def home():
    return Response("Task Scheduler Running")

@app.route("/tasks/log")
def get_task_log():
    try:
        with open("task_log.json", "r") as f:
            logs = json.load(f)
        return Response(json.dumps(logs, indent=2), headers={"Content-Type": "application/json"})
    except FileNotFoundError:
        return Response("No task logs found", status_code=404)

@app.route("/tasks/status")
def get_task_status():
    return Response(f"""
    <!DOCTYPE html>
    <html>
    <head><title>Task Status</title></head>
    <body>
        <h1>Task Scheduler Status</h1>
        <p>Server running since: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><a href="/tasks/log">View Task Logs</a></p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run()
```

## Authentication Middleware

A complete authentication system with middleware:

```python
from future import Future, Response, JSONResponse, Request
from future import Middleware, FutureException
import jwt
import time

# Custom exception
class AuthenticationError(FutureException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)

# Mock user database
users_db = {
    "alice": {"password": "password123", "role": "user"},
    "bob": {"password": "password456", "role": "admin"}
}

# JWT secret (in production, use environment variable)
JWT_SECRET = "your-secret-key"

# Authentication middleware
class AuthMiddleware(Middleware):
    def intercept(self, request: Request) -> Response | None:
        # Skip auth for login endpoint
        if request.path == "/login":
            return None
        
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Missing or invalid Authorization header")
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = payload
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        
        return None

# Admin middleware
class AdminMiddleware(Middleware):
    def intercept(self, request: Request) -> Response | None:
        if not hasattr(request, 'user'):
            raise AuthenticationError("User not authenticated")
        
        if request.user.get("role") != "admin":
            return Response("Admin access required", status_code=403)
        
        return None

# Create application
app = Future()
app.add_middleware(AuthMiddleware)

@app.route("/login", methods=["POST"])
def login(request: Request):
    data = request.json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return Response("Username and password required", status_code=400)
    
    user = users_db.get(username)
    if not user or user["password"] != password:
        return Response("Invalid credentials", status_code=401)
    
    # Create JWT token
    token = jwt.encode({
        "username": username,
        "role": user["role"],
        "exp": time.time() + 3600  # 1 hour expiration
    }, JWT_SECRET, algorithm="HS256")
    
    return JSONResponse({"token": token})

@app.route("/profile")
def get_profile(request: Request):
    return JSONResponse({
        "username": request.user["username"],
        "role": request.user["role"]
    })

@app.route("/admin/users", middleware=[AdminMiddleware])
def admin_users():
    return JSONResponse({
        "users": [
            {"username": username, "role": user["role"]}
            for username, user in users_db.items()
        ]
    })

@app.route("/")
def home():
    return Response("""
    <!DOCTYPE html>
    <html>
    <head><title>Auth Demo</title></head>
    <body>
        <h1>Authentication Demo</h1>
        <div>
            <h2>Login</h2>
            <input type="text" id="username" placeholder="Username">
            <input type="password" id="password" placeholder="Password">
            <button onclick="login()">Login</button>
        </div>
        <div>
            <h2>Profile</h2>
            <button onclick="getProfile()">Get Profile</button>
            <div id="profile"></div>
        </div>
        <div>
            <h2>Admin</h2>
            <button onclick="getUsers()">Get Users (Admin Only)</button>
            <div id="users"></div>
        </div>
        
        <script>
            let token = null;
            
            async function login() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                if (response.ok) {
                    const data = await response.json();
                    token = data.token;
                    alert('Login successful!');
                } else {
                    alert('Login failed!');
                }
            }
            
            async function getProfile() {
                if (!token) {
                    alert('Please login first!');
                    return;
                }
                
                const response = await fetch('/profile', {
                    headers: {'Authorization': `Bearer ${token}`}
                });
                
                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('profile').textContent = JSON.stringify(data);
                } else {
                    alert('Failed to get profile!');
                }
            }
            
            async function getUsers() {
                if (!token) {
                    alert('Please login first!');
                    return;
                }
                
                const response = await fetch('/admin/users', {
                    headers: {'Authorization': `Bearer ${token}`}
                });
                
                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('users').textContent = JSON.stringify(data);
                } else {
                    alert('Failed to get users!');
                }
            }
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run()
```

These examples demonstrate the full range of Future framework capabilities, from simple APIs to complex real-time applications with authentication, GraphQL, and scheduled tasks. 