from ._compat import importlib_metadata

try:
    __version__ = importlib_metadata.version("decocoder")
except importlib_metadata.PackageNotFoundError:
    # TODO: warn / fail here?
    __version__ = "UNKNOWN"
