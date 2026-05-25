class BaseModel:
    def __init__(self, **data):
        annotations = getattr(self, "__annotations__", {})
        for field in annotations:
            if field in data:
                setattr(self, field, data[field])
        for field, value in data.items():
            if field not in annotations:
                setattr(self, field, value)

    def model_dump(self):
        return dict(self.__dict__)

    def dict(self):
        return self.model_dump()


def Field(default=None, **kwargs):
    return default
