# Compatibility shim.
#
# This module exists to preserve backward compatibility with earlier
# versions of the library. Public symbols are re-exported from their
# current implementation locations.
#
# New code should prefer importing from the canonical modules, but
# existing imports will continue to work.

from typeid.core.typeid import PrefixT, TypeID, from_string, from_uuid
from typeid.core.parsing import get_prefix_and_suffix


__all__ = ("PrefixT", "TypeID", "from_string", "from_uuid", "get_prefix_and_suffix")
