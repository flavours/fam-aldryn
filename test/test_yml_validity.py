import subprocess
from pathlib import Path

import libflavour
import pytest
from strictyaml import load


yaml_example_files = [
    ("test/data/addon1_valid1.yml", True),
    ("test/data/addon1_valid2.yml", True),
    ("test/data/addon1_invalid1.yml", False),
    ("test/data/addon1_invalid2.yml", False),
    ("test/data/addon1_invalid3.yml", False),
    ("test/data/addon1_invalid4.yml", False),
    ("test/data/addon1_invalid5.yml", False),
]


@pytest.mark.parametrize("yaml_filename, valid_rego", yaml_example_files)
def test_rego(yaml_filename, valid_rego):
    """
    Test the rego schema definition.
    """
    process = subprocess.Popen(["conftest", "test", yaml_filename])
    outs, errs = process.communicate()
    assert not bool(process.returncode) == valid_rego


@pytest.mark.parametrize("yaml_filename, valid_rego", yaml_example_files)
def test_schema(yaml_filename, valid_rego):
    """
    All our test files are valid flavour schemas. This test just verifies this
    and it is not intended to catch invalid schemas.
    """
    with Path(yaml_filename).open("r") as f:
        load(f.read(), libflavour.schema.schema_addon)
