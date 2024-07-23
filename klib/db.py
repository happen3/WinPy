class Database:
    def __init__(self, maincol: str):
        self.__db__ = {maincol: {}}
        self.__selected__ = maincol

    def select(self, column: str):
        self.__selected__ = column

    def new_column(self, column: str):
        self.__db__[column] = {}

    def delete_column(self, column: str):
        del self.__db__[column]
        self.__selected__ = None if column == self.__selected__ else self.__selected__

    def delete(self, item: str):
        del self.__db__[self.__selected__][item]

    def __setitem__(self, key, value):
        self.__db__[self.__selected__][key] = value

    def __getitem__(self, item):
        return self.__db__[self.__selected__][item]

    def __call__(self):
        return self.__db__


if __name__ == '__main__':
    db = Database("main")
    db.select("main2")
    db.new_column("main2"); db["test"] = "abcdefgh"
    db.select("main")
    db["test"] = "hgfedcba"
    print(db())
    db.delete("test")
    print(db())
    db.delete_column("main")
    print(db())
