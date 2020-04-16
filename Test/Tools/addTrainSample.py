import os

from model.Database import DBSession
from model.models import *

for root, subFolders, files in os.walk("/Users/whexy/Downloads/12306/new"):
    if not subFolders:
        for filename in files:
            train_name = filename.split(".")[0]
            session = DBSession()
            new_train = Train(train_name=train_name)
            session.add(new_train)
            session.commit()
            print("Added " + train_name)
