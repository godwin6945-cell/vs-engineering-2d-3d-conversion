"""
Unit tests for the Secure Sandboxed CAD execution engine.
"""

import pytest
import cadquery as cq
from sketch2step_cad.sandbox import (
    CADSecurityAuditor,
    SecurityViolation,
    execute_sandboxed_cad_script,
    validate_cad_ast,
)


def test_safe_script_passes_ast_validation():
    safe_code = """
import cadquery as cq
import math

result = cq.Workplane("XY").box(100.0, 50.0, 10.0)
"""
    is_safe, violations = validate_cad_ast(safe_code)
    assert is_safe is True
    assert len(violations) == 0


def test_malicious_os_import_blocked():
    bad_code = """
import os
os.system("echo hacked")
"""
    is_safe, violations = validate_cad_ast(bad_code)
    assert is_safe is False
    assert any("os" in v for v in violations)


def test_forbidden_eval_blocked():
    bad_code = """
import cadquery as cq
x = eval("1 + 1")
result = cq.Workplane("XY").box(10, 10, 10)
"""
    is_safe, violations = validate_cad_ast(bad_code)
    assert is_safe is False
    assert any("eval" in v for v in violations)


def test_forbidden_file_open_blocked():
    bad_code = """
f = open("/etc/passwd", "r")
"""
    is_safe, violations = validate_cad_ast(bad_code)
    assert is_safe is False
    assert any("open" in v for v in violations)


def test_dunder_attribute_traversal_blocked():
    bad_code = """
().__class__.__bases__[0].__subclasses__()
"""
    is_safe, violations = validate_cad_ast(bad_code)
    assert is_safe is False
    assert any("__" in v for v in violations)


def test_execute_safe_cad_script():
    safe_script = """
import cadquery as cq

result = (
    cq.Workplane("XY")
    .box(60.0, 40.0, 12.0)
    .faces(">Z")
    .hole(10.0)
)
"""
    solid = execute_sandboxed_cad_script(safe_script)
    assert isinstance(solid, cq.Workplane)
    bb = solid.val().BoundingBox()
    assert abs(bb.xlen - 60.0) < 1e-3
    assert abs(bb.ylen - 40.0) < 1e-3
    assert abs(bb.zlen - 12.0) < 1e-3


def test_execute_malicious_script_raises_security_violation():
    malicious = """
import subprocess
subprocess.run(["ls"])
"""
    with pytest.raises(SecurityViolation):
        execute_sandboxed_cad_script(malicious)
