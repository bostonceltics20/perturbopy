import pytest
import os
from perturbopy import testing_code


def do_tests(testing_args):
    dir_path = os.path.dirname(testing_code.__file__)
    testing_args.insert(0, dir_path)
    result = pytest.main(testing_args)
    return result
