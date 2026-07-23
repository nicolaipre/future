# Docker
Example Compose file for local databases. Copy into a project root (or any folder) and run `docker compose up -d`. Ports bind to `127.0.0.1` only. Point Future `DATABASES` / Settings at these hosts and credentials.

Remove services you do not need before starting.

```yaml
services:

  clickhouse:
    image: clickhouse/clickhouse-server
    container_name: future-clickhouse
    restart: unless-stopped
    ports:
      - "127.0.0.1:8123:8123/tcp"
      - "127.0.0.1:9000:9000/tcp"
    ulimits:
      nofile:
        soft: 262144
        hard: 262144
    environment:
      CLICKHOUSE_DB: future
      CLICKHOUSE_USER: admin
      CLICKHOUSE_PASSWORD: password
    networks:
      - future-net
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    deploy:
      resources:
        limits:
          memory: 2G

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.1
    container_name: future-elasticsearch
    environment:
      - node.name=elasticsearch
      - cluster.name=future-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - xpack.security.enabled=false
      - network.host=0.0.0.0
    ulimits:
      memlock:
        soft: -1
        hard: -1
    ports:
      - "127.0.0.1:9200:9200/tcp"
    networks:
      - future-net
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    deploy:
      resources:
        limits:
          memory: 4G

  mysql:
    image: mysql:8.0
    container_name: future-mysql
    restart: unless-stopped
    ports:
      - "127.0.0.1:3306:3306/tcp"
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: future
    networks:
      - future-net
    volumes:
      - mysql_data:/var/lib/mysql
    deploy:
      resources:
        limits:
          memory: 2G

  postgres:
    image: postgres:15
    container_name: future-postgres
    restart: unless-stopped
    ports:
      - "127.0.0.1:5432:5432/tcp"
    environment:
      POSTGRES_DB: future
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    networks:
      - future-net
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 4G

  redis:
    image: redis:7.0
    container_name: future-redis
    restart: unless-stopped
    ports:
      - "127.0.0.1:6379:6379/tcp"
    networks:
      - future-net
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 4G

  rabbitmq:
    image: rabbitmq:3.11
    container_name: future-rabbitmq
    restart: unless-stopped
    ports:
      - "127.0.0.1:5672:5672/tcp"
    networks:
      - future-net
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    deploy:
      resources:
        limits:
          memory: 4G

  mongodb:
    image: mongo:6.0
    container_name: future-mongodb
    restart: unless-stopped
    ports:
      - "127.0.0.1:27017:27017/tcp"
    networks:
      - future-net
    volumes:
      - mongodb_data:/data/db
    deploy:
      resources:
        limits:
          memory: 4G

networks:
  future-net:

volumes:
  elasticsearch_data:
  clickhouse_data:
  mysql_data:
  postgres_data:
  redis_data:
  rabbitmq_data:
  mongodb_data:
```

## Suggested Settings
| Service | Host | Port | Notes |
|---------|------|------|--------|
| MySQL | `127.0.0.1` | `3306` | root / `password`, database `future` |
| Postgres | `127.0.0.1` | `5432` | `postgres` / `postgres`, database `future` |
| Redis | `127.0.0.1` | `6379` | no password by default |
| MongoDB | `127.0.0.1` | `27017` | |
| Elasticsearch | `127.0.0.1` | `9200` | security disabled (dev only) |
| ClickHouse | `127.0.0.1` | `8123` / `9000` | admin / `password`, database `future` |
| RabbitMQ | `127.0.0.1` | `5672` | optional; not a Future Active Record driver |

SQLite needs no container — use a local file via `DB_DATABASE` / `sqlite_database`. See [Configuration](configuration.md) and [Database](database.md).
