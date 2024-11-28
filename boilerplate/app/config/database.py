from app.config.environment import DB_DRIVER, DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_OPTIONS, DB_DATABASE
from future.database import Database

mysql = Database(
    driver=DB_DRIVER,
    host=DB_HOST,
    port=DB_PORT,
    username=DB_USERNAME,
    password=DB_PASSWORD,
    database=DB_DATABASE,
    options=DB_OPTIONS,
)

database = mysql.session()
