from interfaces.serializable import Serializable

class TaskGraphNode:
    def __init__(self, id: str, label: str):
        self.id = id
        self.label = label
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label
        }