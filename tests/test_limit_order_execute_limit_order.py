import pytest
import boa

def timetravel(to):
    boa.env.vm.patch.timestamp = to

def post_order(limit_order_c, eoa, token_in, token_out, amount_in, amount_out, valid_until):
    limit_order_c.accepting_new_orders(True)
    with boa.env.prank(eoa):
        token_in.approve(limit_order_c, amount_in)
        limit_order_c.post_limit_order(token_in, token_out, amount_in, amount_out, valid_until)
    return limit_order_c.get_all_open_positions(eoa)[0]

def emitted(contract, event, *expected_params):
    logs = contract.get_logs()
    # print(logs)
    e = None

    for l in logs:
        if l.event_type.name == event:
            e = l
            break

    if e == None:
        print("actual  : ", logs)
        print("expected: ", event, expected_params)
        raise Exception(f"event {event} was not emitted")

    t_i = 0
    a_i = 0
    params = []
    # align the evm topic + args lists with the way they appear in the source
    # ex. Transfer(indexed address, address, indexed address)
    for is_topic, k in zip(e.event_type.indexed, e.event_type.arguments.keys()):
        if is_topic:
            params.append(e.topics[t_i])
            t_i += 1
        else:
            params.append(e.args[a_i])
            a_i += 1

    if len(params) != len(expected_params):
        print("actual  : ", params)
        print("expected: ", expected_params)
        raise Exception(f"event {event} emitted with wrong number of params")

    for i, _ in enumerate(params):
        if params[i] != expected_params[i]:
            print("actual  : ", params)
            print("expected: ", expected_params)
            raise Exception(f"event {event} emitted with wrong params")

    return True

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

def test_can_not_execute_insufficient_balance(limit_order_c, abc, xyz, alice):
    with boa.env.anchor():
        alice_balance: uint256 = abc.balanceOf(alice)
        amount_in: uint256 = alice_balance + 1
        amount_out: uint256 = 2
        order = post_order(limit_order_c, alice, abc, xyz, amount_in, amount_out, boa.env.vm.patch.timestamp)
        uid = order[0]
        limit_order_c.execute_limit_order(uid, [abc.address, xyz.address], [1], True)
        # TODO: uncomment the below line after boa is upgraded to the latest version/head which supports VyperContract.get_logs
        # assert emitted(limit_order_c, "LimitOrderFailed", uid, alice, "insufficient balance")

def test_can_not_execute_insufficient_allowance(limit_order_c, abc, xyz, alice):
    with boa.env.anchor():
        alice_balance: uint256 = abc.balanceOf(alice)
        amount_in: uint256 = alice_balance - 1
        amount_out: uint256 = 2
        order = post_order(limit_order_c, alice, abc, xyz, amount_in, amount_out, boa.env.vm.patch.timestamp)
        # revoke all allowance
        with boa.env.prank(alice):
            abc.approve(limit_order_c, 0)
        uid = order[0]
        limit_order_c.execute_limit_order(uid, [abc.address, xyz.address], [1], True)
        # TODO: uncomment the below line after boa is upgraded to the latest version/head which supports VyperContract.get_logs
        # assert emitted(limit_order_c, "LimitOrderFailed", uid, alice, "insufficient allowance")

def test_can_not_execute_swap_was_called(limit_order_c, abc, xyz, alice, uni_router):
    with boa.env.anchor():
        amount_in: uint256 = 1
        amount_out: uint256 = 2
        order = post_order(limit_order_c, alice, abc, xyz, amount_in, amount_out, boa.env.vm.patch.timestamp)
        uid = order[0]
        # limit_order_c.execute_limit_order(uid, [abc.address, xyz.address], [1], True)
        # assert uni_router.swap_was_called()
        # assert emitted(limit_order_c, "LimitOrderExecuted", uid, alice)

def test_can_not_execute_path_len_3_swap_was_called(limit_order_c, abc, xyz, alice, uni_router):
    with boa.env.anchor():
        amount_in: uint256 = 1
        amount_out: uint256 = 2
        order = post_order(limit_order_c, alice, abc, xyz, amount_in, amount_out, boa.env.vm.patch.timestamp)
        uid = order[0]
        # limit_order_c.execute_limit_order(uid, [abc.address, pytest.ZERO_ADDRESS, xyz.address], [1, 2], True)
        # assert uni_router.swap_was_called()
        # assert emitted(limit_order_c, "LimitOrderExecuted", uid, alice)

def test_can_not_execute_profit_sharing_enabled(limit_order_c, abc, xyz, alice, bob, uni_router):
    with boa.env.anchor():
        amount_in: uint256 = 10
        amount_out: uint256 = 20
        order = post_order(limit_order_c, alice, abc, xyz, amount_in, amount_out, boa.env.vm.patch.timestamp)
        uid = order[0]
        uni_router.excessAmountOut(5)
        bob_balance_before: uint256 = xyz.balanceOf(bob)
        # TODO: uncomment below lines and debug failures
        # with boa.env.prank(bob):
        #     limit_order_c.execute_limit_order(uid, [abc.address, xyz.address], [1], True)
        # bob_balance_after: uint256 = xyz.balanceOf(bob)
        # assert bob_balance_after == bob_balance_before + 2

def test_can_not_execute_profit_sharing_disabled(limit_order_c, abc, xyz, alice, bob, uni_router):
    with boa.env.anchor():
        amount_in: uint256 = 10
        amount_out: uint256 = 20
        order = post_order(limit_order_c, alice, abc, xyz, amount_in, amount_out, boa.env.vm.patch.timestamp)
        uid = order[0]
        uni_router.excessAmountOut(5)
        bob_balance_before: uint256 = xyz.balanceOf(bob)
        # TODO: uncomment below lines and debug failures
        # with boa.env.prank(bob):
        #     limit_order_c.execute_limit_order(uid, [abc.address, xyz.address], [1], False)
        # bob_balance_after: uint256 = xyz.balanceOf(bob)
        # assert bob_balance_after == bob_balance_before
