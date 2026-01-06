# Compatibility shim.
#
# This module exists to preserve backward compatibility with earlier
# versions of the library. Public symbols are re-exported from their
# current implementation locations.
#
# New code should prefer importing from the canonical modules, but
# existing imports will continue to work.

from typeid.core.factory import TypeIDFactory, typeid_factory, cached_typeid_factory


__all__ = ("TypeIDFactory", "typeid_factory", "cached_typeid_factory")
