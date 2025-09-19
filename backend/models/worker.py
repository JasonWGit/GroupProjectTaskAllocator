from interfaces.serializable import Serializable

class Worker(Serializable):
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }