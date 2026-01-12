import os

from BACKEND_NAME_PLACEHOLDER import utils

# This Test will fail
def test_00(capfd):
    utils.test()
    out, err = capfd.readouterr()
    assert "This is a test!"+os.linesep == out
    assert "" == err
