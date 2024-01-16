import pytest
from statuses.old_status import *

def test_status_OK():
    completed = Status("Completed", True)
    completed.put_context("lineno", 11)
    completed.put_context("operation", "INSERT")
    assert completed.success
    completed_str = '''OK: Completed
in
  lineno: 11, 
  operation: INSERT.
'''
    assert completed_str == str(completed)

def test_status_ERROR():
    failed = Status("Graphwide Constraint Violated", False)
    failed.put_context("lineno", 11)
    failed.put_context("operation", "INSERT")
    failed.put_context("constraint", "DIRECTED")
    assert not failed.success
    failed_str = '''ERROR: Graphwide Constraint Violated
in
  lineno: 11, 
  operation: INSERT, 
  constraint: DIRECTED.
'''
    assert failed_str == str(failed)

def test_has_errors():
    ok = Status("Completed", True)
    ok2 = Status("Completed", True)
    ok2.put_context("A", 1)
    S = Statuses([ok, ok2])
    assert not S.has_errors()
    failed = Status("FAILED", False)
    S2 = Statuses([ok, failed, ok2])
    assert S2.has_errors()

def test_add_context():
    A = Status("Completed", True)
    B = Status("Completed", True)
    S = Statuses([A, B])
    S.add_context("C", 1)
    assert A["C"] == 1 and B["C"] == 1

def test_merge():
    ok = Status("Completed", True)
    ok2 = Status("Completed", True)
    ok2.put_context("A", 1)
    S = Statuses([ok, ok2])
    failed = Status("FAILED", False)
    S2 = Statuses([ok, failed, ok2])
    S3 = Statuses.merge(S, S2)
    assert(len(S3.statuses)) == 5
    assert S3.statuses[3].message == "FAILED"





