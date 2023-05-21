import pytest
import boa

def test_pause_non_owner_can_not_call(limit_order_c, owner, alice):
    assert limit_order_c.owner() != alice
    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            limit_order_c.pause(True)

def test_pause_noop_call_reverts(limit_order_c, owner):
    with boa.reverts("already in state"):
        limit_order_c.pause(False)
    
    limit_order_c.pause(True)
    assert limit_order_c.is_paused()
    
    with boa.reverts("already in state"):
        limit_order_c.pause(True)

def test_accepting_new_orders_non_owner_can_not_call(limit_order_c, owner, alice):
    assert limit_order_c.owner() != alice
    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            limit_order_c.accepting_new_orders(True)

def test_accepting_new_orders_noop_call_reverts(limit_order_c, owner):
    with boa.reverts("already in state"):
        limit_order_c.accepting_new_orders(False)
    
    limit_order_c.accepting_new_orders(True)
    assert limit_order_c.is_accepting_new_orders()
    
    with boa.reverts("already in state"):
        limit_order_c.accepting_new_orders(True)

def test_suggest_owner_non_owner_can_not_call(limit_order_c, owner, alice, bob):
    assert limit_order_c.owner() != alice
    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            limit_order_c.suggest_owner(bob)

def test_suggest_owner_can_not_suggest_zero_address(limit_order_c, owner, alice, bob):
    with boa.reverts("cannot set owner to zero address"):
        limit_order_c.suggest_owner(pytest.ZERO_ADDRESS)

def test_suggest_owner_can_suggest_non_zero_address(limit_order_c, owner, alice):
    limit_order_c.suggest_owner(alice)
    assert limit_order_c.suggested_owner() == alice

def test_accept_ownership_non_suggested_owner_can_not_call(limit_order_c, owner, alice, bob):
    limit_order_c.suggest_owner(alice)
    with boa.env.prank(bob):
        with boa.reverts("unauthorized"):
            limit_order_c.accept_ownership()

def test_accept_ownership_suggested_owner_can_accept(limit_order_c, owner, alice):
    with boa.env.anchor():
        limit_order_c.suggest_owner(alice)
        assert limit_order_c.owner() == owner
        assert limit_order_c.suggested_owner() == alice
        
        with boa.env.prank(alice):
            limit_order_c.accept_ownership()
        assert limit_order_c.owner() == alice
        assert limit_order_c.suggested_owner() == alice