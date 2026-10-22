from __future__ import annotations

try:
    from .plugin import KshPlugin
except ImportError:  # pragma: no cover
    from plugin import KshPlugin

__all__ = ["KshPlugin"]


def classFactory(iface):
    """QGIS プラグインのエントリーポイント。"""
    return KshPlugin(iface)
