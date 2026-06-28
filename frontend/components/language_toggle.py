"""
Reusable component: language selector widget.
"""

from frontend.components.language_buttons import language_buttons


def language_toggle(key: str = "language_toggle") -> str:
    """
    Render language buttons and return the selected language code.
    """
    return language_buttons(key)
