from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.models import User

engine = create_engine('postgresql://checker:123456@121.36.40.215/cs307')
DBSession = sessionmaker(bind=engine)
session = DBSession()

new_user = User()
new_user.username = 'whexy'
new_user.phone_number = '15052920226'
new_user.real_name = '石文轩'
new_user.email = '11812104@mail.sustech.edu.cn'
new_user.password = 'whexy'
session.add(new_user)
session.commit()
