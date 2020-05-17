from sqlalchemy import func

from model.Database import DBSession


def test():
    session = DBSession()
    try:
        arr = session.execute(func.test_func([1, 2, 3])).first()
        print(arr)
        print(dict(zip(arr.keys(), arr)))
    finally:
        session.close()


if __name__ == '__main__':
    test()
