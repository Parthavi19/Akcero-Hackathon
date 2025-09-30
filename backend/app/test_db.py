# app/test_db.py
from app.db import engine, Base
from app import models
from sqlalchemy import inspect

Base.metadata.create_all(bind=engine)
print("✅ tables created")
print("tables:", inspect(engine).get_table_names())
