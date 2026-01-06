# Compatibility shim.
#
# This module exists to preserve backward compatibility with earlier
# versions of the library. Public symbols are re-exported from their
# current implementation locations.
#
# New code should prefer importing from the canonical modules, but
# existing imports will continue to work.

from typeid.core.constants import PREFIX_MAX_LEN, SUFFIX_LEN, ALPHABET


__all__ = ("PREFIX_MAX_LEN", "SUFFIX_LEN", "ALPHABET")
