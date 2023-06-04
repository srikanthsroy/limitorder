import pytest
import boa

def test_can_not_post_while_paused(limit_order_c, abc, xyz):
    with boa.env.anchor():
        limit_order_c.pause(True)
        with boa.reverts("paused"):
            limit_order_c.post_limit_order(abc, xyz, 1, 2, boa.env.vm.patch.timestamp)

def test_can_not_post_while_not_accepting_new_orders(limit_order_c, abc, xyz):
    with boa.reverts("not accepting new orders"):
        limit_order_c.post_limit_order(abc, xyz, 1, 2, boa.env.vm.patch.timestamp)

def test_can_not_post_order_with_expiry_in_the_past(limit_order_c, abc, xyz):
    with boa.env.anchor():
        limit_order_c.accepting_new_orders(True)
        with boa.reverts("invalid timestamp"):
            limit_order_c.post_limit_order(abc, xyz, 1, 2, boa.env.vm.patch.timestamp - 1)

def test_can_not_post_order_with_insufficient_allowance(limit_order_c, abc, xyz):
    with boa.env.anchor():
        limit_order_c.accepting_new_orders(True)
        with boa.reverts("insufficient allowance"):
            limit_order_c.post_limit_order(abc, xyz, 1, 2, boa.env.vm.patch.timestamp)


def test_post_order_success(limit_order_c, abc, xyz, alice):
    with boa.env.anchor():
        limit_order_c.accepting_new_orders(True)
        with boa.env.prank(alice):
            abc.approve(limit_order_c, 1)
            limit_order_c.post_limit_order(abc, xyz, 1, 2, boa.env.vm.patch.timestamp)
        assert len(limit_order_c.get_all_open_positions(alice)) == 1
        order = limit_order_c.get_all_open_positions(alice)[0]
        assert order[1] == alice
        assert order[2] == abc.address
        assert order[3] == xyz.address
        assert order[4] == 1
        assert order[5] == 2
        assert order[6] == boa.env.vm.patch.timestamp
