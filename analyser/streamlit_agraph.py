import importlib
import sys
from dataclasses import dataclass
from pathlib import Path

import streamlit as st


def _load_external_module():
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


_external_module = _load_external_module()

if _external_module:
    agraph = _external_module.agraph
    Node = _external_module.Node
    Edge = _external_module.Edge
    Config = _external_module.Config
else:
    @dataclass
    class Node:
        id: str
        label: str | None = None
        size: int | None = None
        color: str | None = None

    @dataclass
    class Edge:
        source: str
        target: str
        color: str | None = None

    class Config:
        def __init__(self, **kwargs):
            self.options = kwargs

    def agraph(nodes=None, edges=None, config=None):
        st.info("Grafo indisponivel neste ambiente.")
        return None
