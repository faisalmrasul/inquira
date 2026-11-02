"""UI module — styles, sidebar, workspace, dashboard."""

from .styles import inject_css
from .sidebar import render_sidebar
from .workspace import WORKSPACES, render_workspace
from .dashboard import (
    render_angles,
    render_rai_dashboard,
)

__all__ = [
    "inject_css",
    "render_sidebar",
    "WORKSPACES",
    "render_workspace",
    "render_angles",
    "render_rai_dashboard",
]
