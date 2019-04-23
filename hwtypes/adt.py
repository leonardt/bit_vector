from .adt_meta import TupleMeta, ProductMeta, SumMeta, EnumMeta, is_adt_type

__all__  = ['Tuple', 'Product', 'Sum', 'Enum']
__all__ += ['new', 'new_instruction', 'is_adt_type']

#special sentinal value
class _MISSING: pass

def new(klass, bind=_MISSING, *, name=_MISSING, module=_MISSING):
    class T(klass): pass
    if name is not _MISSING:
        T.__name__ = name
    if module is not _MISSING:
        T.__module__ = module

    if bind is not _MISSING:
        return T[bind]
    else:
        return T

class Tuple(metaclass=TupleMeta):
    def __new__(cls, *value):
        if cls.is_bound:
            return super().__new__(cls)
        else:
            idx = tuple(type(v) for v in value)
            return cls[idx].__new__(cls[idx], *value)

    def __init__(self, *value):
        cls = type(self)
        if len(value) != len(cls.fields):
            raise ValueError('Incorrect number of arguments')
        for v,t in zip(value, cls.fields):
            if not isinstance(v,t):
                raise TypeError('Value {} is not of type {}'.format(repr(v), repr(t)))

        self._value = value

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.value == other.value
        else:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.value)

    def __getitem__(self, idx):
        return self.value[idx]

    def __setitem__(self, idx, value):
        if isinstance(value, type(self)[idx]):
            v = list(self.value)
            v[idx] = value
            self._value = v
        else:
            raise TypeError(f'Value {value} is not of type {type(self)[idx]}')

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f'{type(self).__name__}({",".join(map(repr, self.value))})'

class Product(Tuple, metaclass=ProductMeta):
    def __new__(cls, *args, **kwargs):
        if cls.is_bound:
            return super().__new__(cls, *args, **kwargs)
        elif len(args) == 1:
            #fields, name, bases, namespace
            t = type(cls).from_fields(kwargs, args[0], (cls,), {})
            return t

        else:
            raise TypeError('Cannot instance unbound product type')

    def __repr__(self):
        return f'{type(self).__name__}({",".join(map(repr, self.value))})'

    @property
    def value_dict(self):
        d = {}
        for k in type(self).field_dict:
            d[k] = getattr(self, k)
        return d

class Sum(metaclass=SumMeta):
    def __init__(self, value):
        if type(value) not in type(self).fields and value not in type(self).fields:
            raise TypeError('Value {} is not of types {}'.format(value, type(self).fields))
        self._value = value

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.value == other.value

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.value)

    @property
    def value(self):
        return self._value

    def match(self):
        return type(self.value), self.value

    def __repr__(self) -> str:
        return f'{type(self)}({self.value})'

class Enum(metaclass=EnumMeta):
    def __init__(self, value):
        self._value_ = value

    @property
    def value(self):
        return self._value_

    @property
    def name(self):
        return self._name_

    def __repr__(self):
        return f'{type(self).__name__}.{self.name}'

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.value == other.value

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.value)

def new_instruction():
    return EnumMeta.Auto()
