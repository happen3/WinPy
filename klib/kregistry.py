class Registry:
    def __init__(self):
        self.reg = {}
    def __add__(self, other: dict):
        self.reg.update(other)
    def __getitem__(self, item):
        return self.reg[item]
    def __setitem__(self, key, value: str | bool | int):
        self.reg[key] = value
    def __call__(self):
        return self.reg
    def set(self, indict: dict):
        self.reg = indict
