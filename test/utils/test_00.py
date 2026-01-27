import os

import pytest

from BACKEND_NAME_PLACEHOLDER import utils


def test_00(capfd: pytest.CaptureFixture[str]) -> None:
    utils.test()
    out, err = capfd.readouterr()
    assert "This is a test!" + os.linesep == out
    assert "" == err
