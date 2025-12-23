from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = 'postgresql://postgres:adminadmin@localhost/pdd1'

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(engine)

Base = declarative_base()