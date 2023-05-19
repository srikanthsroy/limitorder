import pytest
import boa

def pytest_configure():
    pytest.ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    pytest.WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

@pytest.fixture(scope="session")
def owner():
    return boa.env.generate_address("owner")

@pytest.fixture(scope="session")
def alice():
    return boa.env.generate_address("alice")

@pytest.fixture(scope="session")
def bob():
    return boa.env.generate_address("bob")

@pytest.fixture(scope="session")
def limit_order_c(owner):
    with boa.env.prank(owner):
        return boa.load("contracts/limit_order.vy")