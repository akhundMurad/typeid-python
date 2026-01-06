# Compatibility shim.
#
# This module exists to preserve backward compatibility with earlier
# versions of the library. Public symbols are re-exported from their
# current implementation locations.
#
# New code should prefer importing from the canonical modules, but
# existing imports will continue to work.

from typeid.core.validation import validate_prefix, validate_suffix_and_decode


__all__ = ("validate_prefix", "validate_suffix_and_decode")
