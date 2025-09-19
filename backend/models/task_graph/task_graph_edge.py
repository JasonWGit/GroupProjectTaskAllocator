from interfaces.serializable import Serializable

class TaskGraphEdge:
    def __init__(self, from_id: str, to_id: str):
        self.from_id = from_id
        self.to_id = to_id

    def to_dict(self) -> dict:
        return {
            "from": self.from_id,
            "to": self.to_id
        }
    
    