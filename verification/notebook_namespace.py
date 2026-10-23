"""Load the official notebook's definitions into one namespace, as the usage example requires."""
import json
import sys
import types
import __future__
from pathlib import Path
from typing import Any, Dict

# The project's official notebook.
NOTEBOOK = "multi_agent_symbolic_discovery_for_financial_fundamental_analysis_draft.ipynb"
# The heading of the first cell that must NOT run: it starts a separate study.
STOP_HEADING = "# Study Assembly"


def load_namespace(root: Path) -> Dict[str, Any]:
    """Execute every code cell before *Study Assembly* and return the shared namespace."""
    notebook = json.loads((root / NOTEBOOK).read_text(encoding="utf-8"))
    # Register a real module so pickling and dataclasses resolve the notebook's classes.
    module = types.ModuleType("__notebook__")
    sys.modules["__notebook__"] = module
    namespace = module.__dict__
    flags = __future__.annotations.compiler_flag
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if source.startswith(STOP_HEADING):
            break
        exec(compile(source, f"<cell {index}>", "exec", flags=flags, dont_inherit=True), namespace)
    return namespace
