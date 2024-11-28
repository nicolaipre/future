from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    def __init__(
        self,
        driver: str,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
        options: str,
    ):
        self.driver = driver
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.options = options

        valid_drivers = ["sqlite", "mysql", "postgresql", "elasticsearch"]
        if self.driver not in valid_drivers:
            raise Exception(
                f"Unsupported driver '{ self.driver }' | Valid drivers are: { valid_drivers }"  # noqa: E501
            )

    def _build_engine_url(self) -> str:
        if self.driver == "sqlite":
            url = f"{ self.driver }+aiosqlite:///{ self.database }"

        elif self.driver == "mysql":
            url = f"{ self.driver }+asyncmy://{ self.username }:\{ self.password }@{ self.host }:{ self.port }/{ self.database }{ self.options if self.options else None }"  # noqa: E501

        elif self.driver == "postgresql":
            url = f"{ self.driver }+asyncpg://{ self.username }:{ self.password }@{ self.host }:{ self.port }/{ self.database }{ self.options if self.options else None }"  # noqa: E501

        elif self.driver == "elasticsearch":
            raise Exception("The Elasticsearch database driver is not yet supported..!")

        return url

    def session(self) -> async_sessionmaker[AsyncSession]:
        # Create the database URL
        url = self._build_engine_url()

        # Create the database engine
        # engine = create_engine(url=url, echo=True)  # env.DB_LOGGING)
        engine = create_async_engine(url=url)

        # Create a global database session object instead of injecting with middleware on every request.
        # session = sessionmaker(bind=engine, expire_on_commit=False)()
        async_session = async_sessionmaker(bind=engine)

        return async_session
