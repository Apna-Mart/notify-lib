class LazyService:
    def __init__(self, factory_func):
        self.factory_func = factory_func
        self.attr_name = f"_{id(self)}"  # Unique name per descriptor

    def __set_name__(self, owner, name):
        self.attr_name = f"_{name}"  # Store it on instance as _sms, _email, etc.

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if not hasattr(instance, self.attr_name):
            setattr(instance, self.attr_name, self.factory_func(instance))
        return getattr(instance, self.attr_name)
