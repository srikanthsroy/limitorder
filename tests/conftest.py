import pytest
import boa

def pytest_configure():
    pytest.ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# conftest account setup
OWNER = boa.env.generate_address("owner")
boa.env.eoa = OWNER

@pytest.fixture(scope="session")
def owner():
    return OWNER

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

@pytest.fixture(scope="session")
def abc_snapshot(alice, bob):
    abc = boa.load(
        "contracts/testing/token/ERC20.vy",
        "Token ABC",
        "ABC",
        18,
        10000 * 10**18,
    )
    abc.transfer(alice, 10 * 10**18)
    abc.transfer(bob, 10 * 10**18)
    return abc

@pytest.fixture()
def abc(abc_snapshot):
    with boa.env.anchor():
        yield abc_snapshot

@pytest.fixture(scope="session")
def xyz_snapshot(alice, bob):
    xyz = boa.load(
        "contracts/testing/token/ERC20.vy",
        "Token XYZ",
        "XYZ",
        18,
        10000 * 10**18,
    )
    xyz.transfer(alice, 10 * 10**18)
    xyz.transfer(bob, 10 * 10**18)
    return xyz

@pytest.fixture()
def xyz(xyz_snapshot):
    with boa.env.anchor():
        yield xyz_snapshot
