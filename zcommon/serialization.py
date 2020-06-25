class SerializableMixinValueError(ValueError):
    pass


class DictionarySerializableMixin:
    """Mixin functions to allow object conversion to dict.
    The result of this functions must represent the object.
    """

    _copy_on_convert = True

    def __encode_as_json_object__(self):
        return self.__to_dictionary__()

    def __to_dictionary__(self):
        """Convert the object to dictionary.
        """
        if isinstance(self, dict):
            return dict(**self) if self._copy_on_convert else self
        raise NotImplementedError()

    @classmethod
    def __from_dictionary__(cls, as_dict: dict):
        """Convert a dictionary representation of the object to the object.
        """
        if issubclass(cls, dict):
            o = cls()
            o.update(as_dict)
            return o
        raise NotImplementedError()
