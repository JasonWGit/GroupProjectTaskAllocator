from typing import Protocol
    
class Serializable(Protocol):
    """
    Protocol for objects that can be serialized to a dictionary.

    Any class that implements this protocol must provide a `to_dict()` method
    that returns a dictionary representation of the object. Useful for converting class instance objects into JSON e.g. for use by vis.js in the frontend
    """

    def to_dict(self) -> dict:
        """
        Convert the object into a dictionary representation.

        Returns:
            dict: A dictionary containing the object's data.
        """
        ...
