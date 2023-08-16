"""
How this works.

In the tests fodler, the test_perturbo.py script runs Perturbo for
a given 'test_name'. The idea is to use the same function (test_perturbo())
to run all of the calc. modes, epr files, etc. All of this should be
happening under the pytest environment (ran by `pytest`).

In this file (conftest.py), we parametrize pytest to make this work.
"""

from perturbopy.test_utils.run_test.run_utils import get_all_tests
from perturbopy.test_utils.run_test.run_utils import filter_tests
from perturbopy.test_utils.run_test.test_driver import clean_epr_folders
import pytest
import os

# define all supplementary arguments for the test running. This function declared in the PyTest itself


def pytest_addoption(parser):

    parser.addoption('--source_folder',
                     help='address of the folder with all reference files for the test performance',
                     nargs="?",
                     required=True)

    parser.addoption('--tags',
                     help='List of tests tags to include in this testsuite run.',
                     nargs='*', default=None)

    parser.addoption('--exclude-tags',
                     help='List of tests tags to exclude from this testsuite run.',
                     nargs='*', default=None)
                     
    parser.addoption('--epr_tags',
                     help='List of epr_tags to include in this testsuite run.',
                     nargs='*', default=None)

    parser.addoption('--exclude-epr_tags',
                     help='List of epr_tags to exclude from this testsuite run.',
                     nargs='*', default=None)

    parser.addoption('--epr',
                     help='List of epr files to test.',
                     nargs='*', default=None)

    parser.addoption('--test-names',
                     help='List of test names to include in this testsuite run.',
                     nargs='*', default=None)

    parser.addoption('--devel',
                     help='Include the development-stage tests.',
                     action='store_true', default=False)

    parser.addoption('--run_qe2pert',
                     help='Include the qe2pert tests',
                     action='store_true')
                     
    parser.addoption('--config_machine',
                     help='Name of file with computational information for qe2pert computation. Should be in the folder tests_f90/comp_qe2pert',
                     nargs="?", default='config_machine.yml')
                     
    parser.addoption('--keep_perturbo',
                     help='Save all the materials related to perturbo tests',
                     action='store_true')
                     
    parser.addoption('--keep_epr',
                     help='Save all epr-files from the qe2pert testing',
                     action='store_true')
                     
    parser.addoption('--keep_preliminary',
                     help='Save all preliminary files for epr files calculations',
                     action='store_true')

# generation of test for each type of test function. This function automatically called,
# when we run tests from the subfolders of folder, where this function is saved.


def pytest_generate_tests(metafunc):
    """
    The purpose of this function is to feed multiple test names to the
    tests/test_perturbo.py test_perturbo(test_name) function.
    Here, this function is referred as 'metafunc'.

    First, we get the list of all of the test folders using the tests/epr_info.yml file.
    We retrieve the test folder as <epr name>-<test name>. This is done by the get_all_tests()
    function.

    Next, we remove some of the tests based on the command line options and obtain the target
    test_list using the filer_tests() function.

    Finally, we feed the elements of the test_list to the test_perturbo() (metafunction)
    as the test_name input argument of the function.
    """
    if 'test_name' in metafunc.fixturenames:
        
        # define folder with supplementary information
        source_folder = os.path.abspath(metafunc.config.getoption('source_folder'))

        # Get the list of all test folders
        all_test_list, all_dev_test_list = get_all_tests(metafunc.function.__name__, source_folder)

        # Add the devel tests if --devel was specified
        if metafunc.config.getoption('devel'):
            all_test_list += all_dev_test_list

        if (metafunc.function.__name__ == 'test_perturbo') or (metafunc.function.__name__ == 'test_perturbo_for_qe2pert'):
            # sort out test folders based on command-line options (if present)
            test_list = filter_tests(
                all_test_list,
                metafunc.config.getoption('tags'),
                metafunc.config.getoption('exclude_tags'),
                metafunc.config.getoption('epr'),
                metafunc.config.getoption('test_names'),
                metafunc.function.__name__,
                metafunc.config.getoption('run_qe2pert'),
                source_folder
            )
        elif (metafunc.function.__name__ == 'test_qe2pert'):
            test_list = filter_tests(
                all_test_list,
                metafunc.config.getoption('epr_tags'),
                metafunc.config.getoption('exclude_epr_tags'),
                metafunc.config.getoption('epr'),
                None,
                metafunc.function.__name__,
                metafunc.config.getoption('run_qe2pert'),
                source_folder
            )
        
        if metafunc.function.__name__ == 'test_perturbo_for_qe2pert':
            metafunc.parametrize('test_name', test_list, indirect=True)
            metafunc.parametrize('config_machine', [metafunc.config.getoption('config_machine')], indirect=True)
            metafunc.parametrize('keep_perturbo', [metafunc.config.getoption('keep_perturbo')], indirect=True)
            metafunc.parametrize('run_qe2pert', [metafunc.config.getoption('run_qe2pert')], indirect=True)
            metafunc.parametrize('source_folder', [source_folder], indirect=True)
        elif metafunc.function.__name__ == 'test_qe2pert':
            metafunc.parametrize('test_name', test_list, indirect=True)
            metafunc.parametrize('run_qe2pert', [metafunc.config.getoption('run_qe2pert')], indirect=True)
            metafunc.parametrize('config_machine', [metafunc.config.getoption('config_machine')], indirect=True)
            metafunc.parametrize('source_folder', [source_folder], indirect=True)
        elif metafunc.function.__name__ == 'test_perturbo':
            metafunc.parametrize('test_name', test_list, indirect=True)
            metafunc.parametrize('config_machine', [metafunc.config.getoption('config_machine')], indirect=True)
            metafunc.parametrize('keep_perturbo', [metafunc.config.getoption('keep_perturbo')], indirect=True)
            metafunc.parametrize('source_folder', [source_folder], indirect=True)
        
# in order to properly run pytest functions, we need to declare fixtures,
# which allow us to use parametrization of test functions


@pytest.fixture
def test_name(request):
    return request.param
    

@pytest.fixture
def run_qe2pert(request):
    return request.param


@pytest.fixture
def config_machine(request):
    return request.param
    

@pytest.fixture
def keep_perturbo(request):
    return request.param


@pytest.fixture
def source_folder(request):
    return request.param

# this is predefined function of PyTest, which is runned after the end of all tests.
# here we delete all epr-folders, for which all tests were passed


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if config.getoption('run_qe2pert'):
        if exitstatus == 0:
            # delete all epr files
            epr_failed = []
        else:
            failed_reports = terminalreporter.getreports('failed')
            # Process the list of failed test reports as needed
            epr_failed = set()
            for report in failed_reports:
                # obtain epr-name of failed test
                epr_failed.add(report.nodeid.split("[")[1].rstrip("]").split('-')[0])
            epr_failed = list(epr_failed)
    
        clean_epr_folders(epr_failed, config.getoption('config_machine'), config.getoption('keep_epr'),
                          config.getoption('keep_preliminary'), os.path.abspath(config.getoption('source_folder')))
