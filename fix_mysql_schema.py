import config
from sqlalchemy import create_engine, inspect, text

engine = create_engine(config.MYSQL_CONN)
inspector = inspect(engine)

mysql_table = "hosonhanvien"
if mysql_table not in inspector.get_table_names():
    raise SystemExit(f"Table {mysql_table} does not exist in MySQL database")

columns = [col["name"] for col in inspector.get_columns(mysql_table)]
print("Current columns:", columns)

with engine.begin() as conn:
    if "DiaChi" not in columns:
        print("Adding missing column DiaChi to hosonhanvien...")
        conn.execute(text("ALTER TABLE hosonhanvien ADD COLUMN DiaChi VARCHAR(255) NULL"))
        print("Added DiaChi")
    else:
        print("Column DiaChi already exists")

    if "PhongBan" in columns and columns.count("PhongBan") == 1:
        # No action, just sanity check
        pass

print("MySQL schema check complete.")
