import importlib
import sys
from pathlib import Path

import streamlit as st


def _load_external_aggrid():
    current_dir = Path(__file__).resolve().parent
    current_module = sys.modules.get(__name__)
    original_path = list(sys.path)

    try:
        sys.path = [
            entry for entry in sys.path
            if entry and Path(entry).resolve() != current_dir
        ]
        sys.modules.pop(__name__, None)
        return importlib.import_module(__name__)
    except Exception:
        return None
    finally:
        sys.path = original_path
        if current_module:
            sys.modules[__name__] = current_module


_external_aggrid = _load_external_aggrid()

if _external_aggrid:
    AgGrid = _external_aggrid.AgGrid
    GridOptionsBuilder = _external_aggrid.GridOptionsBuilder
    GridUpdateMode = _external_aggrid.GridUpdateMode
else:
    class GridUpdateMode:
        SELECTION_CHANGED = "SELECTION_CHANGED"

    class GridOptionsBuilder:
        def __init__(self, dataframe):
            self.dataframe = dataframe
            self.options = {}

        @classmethod
        def from_dataframe(cls, dataframe):
            return cls(dataframe)

        def configure_pagination(self, **kwargs):
            self.options.setdefault("pagination", {}).update(kwargs)

        def configure_column(self, *args, **kwargs):
            self.options.setdefault("columns", []).append((args, kwargs))

        def configure_selection(self, **kwargs):
            self.options["selection"] = kwargs

        def build(self):
            return self.options

    def AgGrid(
        dataframe,
        gridOptions=None,
        enable_enterprise_modules=False,
        update_mode=None,
        theme=None,
        **kwargs,
    ):
        st.dataframe(dataframe, use_container_width=True, hide_index=True)
        return {"selected_rows": []}
