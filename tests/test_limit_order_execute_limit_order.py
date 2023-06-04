import pytest
import boa

def timetravel(to):
    boa.env.vm.patch.timestamp = to

def post_order(limit_order_c, eoa, token_in, token_out, amount_in, amount_out, valid_until):
    limit_order_c.accepting_new_orders(True)
    with boa.env.prank(eoa):
        token_in.approve(limit_order_c, 1)
        limit_order_c.post_limit_order(token_in, token_out, amount_in, amount_out, valid_until)
    return limit_order_c.get_all_open_positions(eoa)[0]

def test_can_not_execute_while_paused(limit_order_c, abc, xyz):
    with boa.env.anchor():
        limit_order_c.pause(True)
        with boa.reverts("paused"):
            limit_order_c.execute_limit_order(bytes(0), [abc.address, xyz.address], [0], True)

def test_can_not_execute_expired_order(limit_order_c, abc, xyz, alice):
    with boa.env.anchor():
        order = post_order(limit_order_c, alice, abc, xyz, 1, 2, boa.env.vm.patch.timestamp)
        uid = order[0]
        timetravel(boa.env.vm.patch.timestamp + 1)
        with boa.reverts("order expired"):
            limit_order_c.execute_limit_order(uid, [abc.address, xyz.address], [0], True)

def test_can_not_execute_invalid_path_len(limit_order_c, abc, xyz, alice):
    with boa.env.anchor():
        order = post_order(limit_order_c, alice, abc, xyz, 1, 2, boa.env.vm.patch.timestamp)
        uid = order[0]
        with boa.reverts("[path] invlid path"):
            limit_order_c.execute_limit_order(uid, [], [0], True)
        with boa.reverts("[path] invlid path"):
            limit_order_c.execute_limit_order(uid, [abc.address], [0], True)

def test_can_not_execute_invalid_fees_len(limit_order_c, abc, xyz, alice):
    with boa.env.anchor():
        order = post_order(limit_order_c, alice, abc, xyz, 1, 2, boa.env.vm.patch.timestamp)
        uid = order[0]
        with boa.reverts("[path] invalid fees"):
            limit_order_c.execute_limit_order(uid, [abc.address, xyz.address], [], True)
        with boa.reverts("[path] invalid fees"):
            limit_order_c.execute_limit_order(uid, [abc.address, xyz.address], [1, 1], True)
        with boa.reverts("[path] invalid fees"):
            limit_order_c.execute_limit_order(uid, [abc.address, pytest.ZERO_ADDRESS, xyz.address], [], True)
        with boa.reverts("[path] invalid fees"):
            limit_order_c.execute_limit_order(uid, [abc.address, pytest.ZERO_ADDRESS, xyz.address], [1], True)

def test_can_not_execute_invalid_token_in(limit_order_c, abc, xyz, alice):
    with boa.env.anchor():
        order = post_order(limit_order_c, alice, abc, xyz, 1, 2, boa.env.vm.patch.timestamp)
        uid = order[0]
        with boa.reverts("[path] invalid token_in"):
            limit_order_c.execute_limit_order(uid, [xyz.address, abc.address], [1], True)

def test_can_not_execute_invalid_token_out(limit_order_c, abc, xyz, alice):
    with boa.env.anchor():
        order = post_order(limit_order_c, alice, abc, xyz, 1, 2, boa.env.vm.patch.timestamp)
        uid = order[0]
        with boa.reverts("[path] invalid token_out"):
            limit_order_c.execute_limit_order(uid, [abc.address, abc.address], [1], True)
