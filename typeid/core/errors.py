class TypeIDException(Exception):
    ...


class PrefixValidationException(TypeIDException):
    ...


class SuffixValidationException(TypeIDException):
    ...


class InvalidTypeIDStringException(TypeIDException):
    ...
