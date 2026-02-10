from abc import ABC, abstractmethod

# --- Codebase for Factory ---
class Shape(ABC):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @abstractmethod
    def draw(self) -> str:
        pass

class _ShapeFactory:
    """Pure Creation (Internal Use Only)"""
    _blueprints = {}

    @classmethod
    def create(cls, name:str, **default_attrs):
        """Creates a new SubClass of Shape Abstract Class"""
        class_name = name.capitalize()

        # Define Standart Methods for SubClasses
        def draw(self):
            return f"I am a {class_name} with properties: {self.__dict__}"
        
        # Combine Attributes
        class_attributes = {**default_attrs, "draw":draw}

        # use 'type' to manufacture the class
        product_class = type(class_name, (Shape,), class_attributes)

        # Store in archive
        # Return new class
        cls._blueprints[name.lower()] = product_class
        return product_class
    
    @classmethod
    def get_blueprints(cls):
        return cls._blueprints
    
    @classmethod
    def clear(cls):
        cls._blueprints.clear()

class ShapeRegistry:
    _instances = {}
    """Stores instances and orchestrates creation of new subclasses"""
    @classmethod
    def get_instance(cls, name: str, **kwargs) -> Shape:
        # normalize
        name = name.lower()

        # Check for instance
        if name not in cls._instances:
            # Verify blueprint available
            if name not in _ShapeFactory._blueprints:
                # Create New Class
                _ShapeFactory.create(name)

            # Grab class prototype from _Factory
            # Get instance and apply parameters
            prototype   = _ShapeFactory._blueprints[name]
            instance    = prototype(**kwargs)

            # Store instance in registry
            cls._instances[name] = instance
        
        # Return instance from registry
        return cls._instances[name]

    @classmethod
    def list_inventory(cls):
        return list(cls._instances.keys())

# --- Implementing Tests ---
def test_factory():
    #base = Shape()
    triangle = ShapeRegistry.get_instance("triangle", size=3, perimiter=24)
    inventory = ShapeRegistry.list_inventory()
    print(inventory)
    print(triangle.draw())
