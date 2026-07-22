from textwrap import dedent

import strawberry


# Sample data
db_users = [
    {"id": "1", "name": "Alice", "email": "alice@example.com"},
    {"id": "2", "name": "Bob", "email": "bob@example.com"},
    {"id": "3", "name": "Charlie", "email": "charlie@example.com"},
]

db_posts = [
    {"id": "101", "title": "GraphQL vs REST", "content": "GraphQL is amazing!", "author_id": "1"},
    {"id": "102", "title": "Strawberry Rocks", "content": "Strawberry is great for Python!", "author_id": "2"},
]


# GraphQL queries
queries = {
    "GetEverything": dedent("""
        query GetEverything {
            users {
                id
                name
                email
            }
            posts {
                id
                title
                content
                author {
                    id
                    name
                    email
                }
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]
    "GetAllUsers": dedent("""
        query GetAllUsers {
            users {
                id
                name
                email
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]
    "GetAllPosts": dedent("""
        query GetAllPosts {
            posts {
                id
                title
                content
                author {
                    id
                    name
                    email
                }
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]
    "GetPostsWithAuthors": dedent("""
        query GetPostsWithAuthors {
            posts {
                id
                title
                content
                author {
                    name
                    email
                }
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]
    "GetTitlesAndAuthors": dedent("""
        query GetTitlesAndAuthors {
            posts {
                title
                author {
                    name
                }
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]
    "GetEmails": dedent("""
        query GetEmails {
            users {
                email
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]
}


# Define GraphQL types
class User:
    id: str
    name: str
    email: str

    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email


class Post:
    id: str
    title: str
    content: str
    author: "User"

    def __init__(self, id: str, title: str, content: str, author: "User"):
        self.id = id
        self.title = title
        self.content = content
        self.author = author


# Create Strawberry types
UserType = strawberry.type(User)
PostType = strawberry.type(Post)


# Define resolvers
async def resolve_users() -> list[UserType]:  # type: ignore[misc,valid-type]
    return [UserType(id=u["id"], name=u["name"], email=u["email"]) for u in db_users]


async def resolve_posts() -> list[PostType]:  # type: ignore[misc,valid-type]
    posts = []
    for p in db_posts:
        author = next(u for u in db_users if u["id"] == p["author_id"])
        user = UserType(id=author["id"], name=author["name"], email=author["email"])
        post = PostType(id=p["id"], title=p["title"], content=p["content"], author=user)
        posts.append(post)
    return posts


# Define Query type
class Query:
    users = strawberry.field(resolver=resolve_users)
    posts = strawberry.field(resolver=resolve_posts)


# NB:!!!!  schema cannot be instantiated in the controller. it breaks then.
schema = strawberry.Schema(query=strawberry.type(Query))
