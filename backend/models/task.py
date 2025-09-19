from interfaces.serializable import Serializable

class Task(Serializable):
    def __init__(self, id: str, name: str, description: str, duration: int, dependencies: list[str]):
        self.id = id
        self.name = name
        self.description = description
        self.duration = duration
        self.dependencies = dependencies

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "dependencies": self.dependencies
        }
    
    

    