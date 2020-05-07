from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# engine = create_engine('postgresql://checker:123456@121.36.40.215/cs307', encoding="utf-8")
engine = create_engine(
    'postgresql://checker:123456@121.36.40.215/cs307',
    pool_recycle=7200,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    encoding="utf-8")
DBSession = sessionmaker(bind=engine)
