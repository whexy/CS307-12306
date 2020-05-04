from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://checker:123456@121.36.40.215/cs307', encoding="utf-8")
# engine = create_engine('postgresql://checker:123456@121.36.40.215/cs307', encoding="utf-8", echo=True)
DBSession = sessionmaker(bind=engine)
