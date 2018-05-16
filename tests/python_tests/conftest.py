import pytest

import xchainer
import xchainer.testing

from tests import cuda_utils


def pytest_generate_tests(metafunc):
    if hasattr(metafunc.function, 'parametrize_device'):
        device_names, = metafunc.function.parametrize_device.args
        metafunc.parametrize('device', device_names, indirect=True)


def _get_required_cuda_devices_from_device_name(device_name):
    # Returns the number of required CUDA devices to run a test, given a device name.
    # If the device is non-CUDA device, 0 is returned.
    s = device_name.split(':')
    assert len(s) == 2
    if s[0] != 'cuda':
        return 0
    return int(s[1]) + 1


@pytest.fixture
def device(request):
    # A fixture to wrap a test with a device scope, given a device name.
    # Device instance is passed to the test.

    device_name = request.param

    # Skip if the device is CUDA device and there's no sufficient CUDA devices.
    cuda_device_count = _get_required_cuda_devices_from_device_name(device_name)
    if cuda_device_count > cuda_utils.get_cuda_limit():
        pytest.skip()

    device = xchainer.get_device(device_name)
    device_scope = xchainer.device_scope(device)

    def finalize():
        device_scope.__exit__()

    request.addfinalizer(finalize)
    device_scope.__enter__()
    return device


@pytest.fixture(params=xchainer.testing.all_dtypes)
def dtype(request):
    return request.param


@pytest.fixture(params=xchainer.testing.float_dtypes)
def float_dtype(request):
    return request.param


@pytest.fixture(params=xchainer.testing.signed_dtypes)
def signed_dtype(request):
    return request.param


@pytest.fixture(params=xchainer.testing.numeric_dtypes)
def numeric_dtype(request):
    return request.param


@pytest.fixture(params=[True, False])
def is_module(request):
    return request.param
