import importlib
import sys
from pathlib import Path

import streamlit as st


def _load_external_option_menu():
    current_dir = Path(__file__).resolve().parent
    current_module = sys.modules.get(__name__)
    original_path = list(sys.path)

    try:
        sys.path = [
            entry for entry in sys.path
            if entry and Path(entry).resolve() != current_dir
        ]
        sys.modules.pop(__name__, None)
        module = importlib.import_module(__name__)
        return getattr(module, "option_menu", None)
    except Exception:
        return None
    finally:
        sys.path = original_path
        if current_module:
            sys.modules[__name__] = current_module


_external_option_menu = _load_external_option_menu()


def option_menu(
    menu_title,
    options,
    icons=None,
    menu_icon=None,
    default_index=0,
    orientation="vertical",
    **kwargs,
):
    if _external_option_menu:
        return _external_option_menu(
            menu_title,
            options,
            icons=icons,
            menu_icon=menu_icon,
            default_index=default_index,
            orientation=orientation,
            **kwargs,
        )

    label = menu_title or "Menu"
    return st.radio(
        label,
        options,
        index=default_index,
        horizontal=orientation == "horizontal",
        label_visibility="visible" if menu_title else "collapsed",
    )
