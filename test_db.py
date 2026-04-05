import config
from sqlalchemy import create_engine, text

print("Testing database connections...")

try:
    # Test SQL Server connection
    sql_engine = create_engine(config.SQL_SERVER_CONN)
    with sql_engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        print("✅ SQL Server connection successful")

    # Test MySQL connection
    mysql_engine = create_engine(config.MYSQL_CONN)
    with mysql_engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        print("✅ MySQL connection successful")

    print("🎉 All database connections are working!")

except Exception as e:
    print(f"❌ Database connection error: {e}")
    print("Please check your database configurations and ensure databases are running.")