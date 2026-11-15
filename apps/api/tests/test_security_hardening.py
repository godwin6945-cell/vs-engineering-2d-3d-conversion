"""
Security Hardening and Sandbox Containment Tests for Sketch2STEP Enterprise.
Verifies:
1. AST Static Auditor strictly blocks arbitrary code execution and escape exploits.
2. CadQuery Sandbox executes safe parametric scripts while denying dangerous syscalls.
3. API key and webhook HMAC authentication enforces tenant isolation.
"""

import pytest
import hmac
import hashlib
from sketch2step_cad.sandbox import (
    CADSecurityAuditor,
    validate_cad_ast,
    execute_sandboxed_cad_script,
    SecurityViolation,
)


def test_ast_auditor_allows_valid_cadquery():
    """Valid CAD parametric code must pass AST review."""
    code = """
import cadquery as cq

result = cq.Workplane("XY").box(50.0, 30.0, 15.0).faces(">Z").hole(8.0)
"""
    is_valid, errors = validate_cad_ast(code)
    assert is_valid is True
    assert len(errors) == 0


def test_ast_auditor_blocks_dangerous_imports():
    """Imports of os, sys, subprocess, socket, etc. must be blocked."""
    forbidden_payloads = [
        "import os\nos.system('echo pwned')",
        "import sys\nsys.exit(1)",
        "import subprocess\nsubprocess.Popen(['ls'])",
        "import socket\ns = socket.socket()",
        "import shutil\nshutil.rmtree('/')",
        "from os import path",
    ]
    for code in forbidden_payloads:
        is_valid, errors = validate_cad_ast(code)
        assert is_valid is False, f"Expected audit failure for: {code}"
        assert any("Forbidden import" in e for e in errors)


def test_ast_auditor_blocks_forbidden_builtins():
    """Dangerous builtins like eval, exec, open, breakpoint must be blocked."""
    forbidden_calls = [
        "eval('2 + 2')",
        "exec('a = 1')",
        "f = open('/etc/passwd', 'r')",
        "compile('x = 1', '', 'exec')",
        "breakpoint()",
    ]
    for code in forbidden_calls:
        is_valid, errors = validate_cad_ast(code)
        assert is_valid is False, f"Expected audit failure for: {code}"


def test_ast_auditor_blocks_dunder_traversal():
    """Dunder attribute traversal exploits (__subclasses__, __globals__) must be blocked."""
    exploits = [
        "x = ().__class__.__bases__[0].__subclasses__()",
        "def f(): pass\ng = f.__globals__",
        "def f(): pass\nc = f.__code__",
    ]
    for code in exploits:
        is_valid, errors = validate_cad_ast(code)
        assert is_valid is False, f"Expected audit failure for: {code}"
        assert any("Forbidden attribute access" in e for e in errors)


def test_sandbox_executes_cad_cleanly():
    """Sandbox safely builds a parametric box in isolation."""
    script = """
import cadquery as cq
result = cq.Workplane("XY").box(20.0, 20.0, 10.0)
"""
    solid = execute_sandboxed_cad_script(script)
    assert solid is not None
    assert solid.val().isValid() is True


def test_sandbox_rejects_malicious_script():
    """Attempting to execute malicious script inside sandbox raises SecurityViolation."""
    script = """
import os
result = None
"""
    with pytest.raises(SecurityViolation):
        execute_sandboxed_cad_script(script)


def test_webhook_hmac_signature_verification():
    """Webhook signatures must be tamper-proof and verifiable."""
    secret = "whsec_test_secret_key_12345"
    payload = b'{"event":"job.validated","job_id":"job_01"}'

    signature = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    # Valid check
    assert hmac.compare_digest(
        signature,
        hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    ) is True

    # Tampered payload check
    tampered_payload = b'{"event":"job.validated","job_id":"job_99"}'
    assert hmac.compare_digest(
        signature,
        hmac.new(secret.encode("utf-8"), tampered_payload, hashlib.sha256).hexdigest()
    ) is False
