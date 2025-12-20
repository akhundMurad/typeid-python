"""
Schema discovery for `typeid explain`.

This module implements a conservative, non-breaking discovery mechanism:
- If nothing is found, callers proceed without schema (feature still works).
- No new mandatory dependencies.
- Paths are resolved deterministically with clear precedence.

Precedence (first match wins):
1) explicit CLI arg: --schema PATH (handled by caller; use discover_schema only if not provided)
2) environment variable: TYPEID_SCHEMA
3) current working directory:
     - typeid.schema.json
     - typeid.schema.yaml / typeid.schema.yml
4) user config directory:
     - <config_dir>/typeid/schema.json
     - <config_dir>/typeid/schema.yaml / schema.yml
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

DEFAULT_CWD_CANDIDATES = (
    "typeid.schema.json",
    "typeid.schema.yaml",
    "typeid.schema.yml",
)

DEFAULT_USER_CANDIDATES = (
    "schema.json",
    "schema.yaml",
    "schema.yml",
)


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    """Result of schema discovery."""

    path: Optional[Path]
    source: str  # e.g., "env:TYPEID_SCHEMA", "cwd", "user_config", "none"


def discover_schema_path(
    *,
    env_var: str = "TYPEID_SCHEMA",
    cwd: Optional[Path] = None,
) -> DiscoveryResult:
    """
    Discover schema file path using the configured precedence rules.

    Args:
        env_var: environment variable name to check first.
        cwd: optional cwd override (useful for tests).

    Returns:
        DiscoveryResult with found path or None.
    """
    # 1) Environment variable
    env_value = os.environ.get(env_var)
    if env_value:
        p = Path(env_value).expanduser()
        if p.is_file():
            return DiscoveryResult(path=p, source=f"env:{env_var}")
        # If provided but invalid, we treat it as "not found" but caller can
        # warn separately if they want.
        return DiscoveryResult(path=None, source=f"env:{env_var} (not found)")

    # 2) Current working directory
    cwd_path = cwd or Path.cwd()
    for name in DEFAULT_CWD_CANDIDATES:
        p = cwd_path / name
        if p.is_file():
            return DiscoveryResult(path=p, source="cwd")

    # 3) User config directory
    user_cfg = _user_config_dir()
    if user_cfg is not None:
        base = user_cfg / "typeid"
        for name in DEFAULT_USER_CANDIDATES:
            p = base / name
            if p.is_file():
                return DiscoveryResult(path=p, source="user_config")

    return DiscoveryResult(path=None, source="none")


def _user_config_dir() -> Optional[Path]:
    """
    Return OS-appropriate user config directory.

    - Linux/macOS: ~/.config
    - Windows: %APPDATA%
    """
    # Windows: APPDATA is the typical location for roaming config
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata).expanduser()

    # XDG on Linux, also often present on macOS
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser()

    # Fallback to ~/.config
    home = Path.home()
    if home:
        return home / ".config"
    return None


def iter_default_candidate_paths(*, cwd: Optional[Path] = None) -> Iterable[Path]:
    """
    Yield all candidate paths in discovery order (excluding env var).

    Useful for debugging or `typeid explain --debug-discovery` style features.
    """
    cwd_path = cwd or Path.cwd()
    for name in DEFAULT_CWD_CANDIDATES:
        yield cwd_path / name

    user_cfg = _user_config_dir()
    if user_cfg is not None:
        base = user_cfg / "typeid"
        for name in DEFAULT_USER_CANDIDATES:
            yield base / name
