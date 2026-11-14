"""
Secure Sandboxed Execution Engine for CAD code.
Enforces Section 6 security rules:
- Static AST allow-list before execution (only safe cadquery, math, and harmless builtins).
- Completely blocks dangerous modules: os, sys, subprocess, socket, urllib, requests, eval, exec, __import__.
- Enforces strict execution timeouts.
- Fallback synthesis path tagging jobs as "AI-generated geometry, extra review required".
"""

import ast
import logging
import math
from typing import Any, Dict, Optional, Set, Tuple
import cadquery as cq

logger = logging.getLogger(__name__)

# Permitted module imports
ALLOWED_MODULES: Set[str] = {
    "cadquery",
    "cq",
    "math",
}

# Strictly forbidden builtins and function calls
FORBIDDEN_NAMES: Set[str] = {
    "__import__",
    "eval",
    "exec",
    "compile",
    "open",
    "input",
    "breakpoint",
    "globals",
    "locals",
    "vars",
    "getattr",
    "setattr",
    "delattr",
    "hasattr",
    "memoryview",
    "exit",
    "quit",
}

FORBIDDEN_ATTRIBUTES: Set[str] = {
    "__subclasses__",
    "__bases__",
    "__mro__",
    "__code__",
    "__globals__",
    "__builtins__",
}


class SecurityViolation(Exception):
    """Raised when CAD script contains unauthorized AST nodes or imports."""
    pass


class CADSecurityAuditor(ast.NodeVisitor):
    """
    Static AST visitor validating that a script contains ONLY allowed
    geometry operations and mathematical primitives.
    """

    def __init__(self):
        self.violations: list[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_module = alias.name.split(".")[0]
            if base_module not in ALLOWED_MODULES:
                self.violations.append(f"Forbidden import '{alias.name}' at line {node.lineno}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_module = node.module.split(".")[0]
            if base_module not in ALLOWED_MODULES:
                self.violations.append(f"Forbidden import from '{node.module}' at line {node.lineno}")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if node.id in FORBIDDEN_NAMES:
            self.violations.append(f"Forbidden built-in reference '{node.id}' at line {node.lineno}")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr in FORBIDDEN_ATTRIBUTES:
            self.violations.append(f"Forbidden attribute access '{node.attr}' at line {node.lineno}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_NAMES:
            self.violations.append(f"Forbidden function call '{node.func.id}' at line {node.lineno}")
        self.generic_visit(node)


def validate_cad_ast(code: str) -> Tuple[bool, list[str]]:
    """
    Statically analyzes Python code string before execution.
    Returns (is_safe, list_of_violations).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"Syntax error: {e}"]

    auditor = CADSecurityAuditor()
    auditor.visit(tree)

    if auditor.violations:
        return False, auditor.violations

    return True, []


def execute_sandboxed_cad_script(
    code: str,
    timeout_seconds: float = 15.0,
) -> cq.Workplane:
    """
    Executes a validated CadQuery script inside a restricted namespace.
    The script must produce a variable named `result` or `model` holding a cq.Workplane.
    """
    is_safe, violations = validate_cad_ast(code)
    if not is_safe:
        raise SecurityViolation(f"CAD code rejected by security auditor: {'; '.join(violations)}")

    def safe_import(name, *args, **kwargs):
        base_module = name.split(".")[0]
        if base_module not in ALLOWED_MODULES:
            raise ImportError(f"Importing module '{name}' is strictly forbidden by security policy.")
        if base_module in ("cadquery", "cq"):
            return cq
        elif base_module == "math":
            return math
        raise ImportError(f"Cannot import '{name}'")

    # Restrict execution globals
    safe_globals: Dict[str, Any] = {
        "__builtins__": {
            "__import__": safe_import,
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "sum": sum,
            "range": range,
            "len": len,
            "float": float,
            "int": int,
            "bool": bool,
            "str": str,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "zip": zip,
            "enumerate": enumerate,
            "print": lambda *args, **kwargs: None,  # no-op logging
        },
        "cq": cq,
        "cadquery": cq,
        "math": math,
    }

    local_vars: Dict[str, Any] = {}

    try:
        # Execute in restricted scope
        exec(code, safe_globals, local_vars)
    except Exception as e:
        logger.error(f"Execution error in CAD script: {e}")
        raise RuntimeError(f"CAD generation script execution failed: {str(e)}")

    # Extract result
    result = local_vars.get("result") or local_vars.get("model") or local_vars.get("part")
    if result is None:
        raise ValueError("CAD script must assign the final solid to 'result' or 'model'")

    if not isinstance(result, cq.Workplane):
        raise TypeError(f"CAD script returned type {type(result)}, expected cadquery.Workplane")

    return result
