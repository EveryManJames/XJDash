"""Tests for relay control safety logic (runs against the mock relay)."""
from relay.relay_controller import RelayController


def make_controller():
    """Controller that always lands on the mock (nonexistent port)."""
    rc = RelayController(config={'port': '/dev/nonexistent-test-port'})
    rc.connect()
    assert rc.is_mock
    return rc


def test_falls_back_to_mock_without_hardware():
    rc = make_controller()
    assert rc.connected
    rc.disconnect()


def test_set_and_read_cached():
    rc = make_controller()
    assert rc.get_cached(1) is False
    assert rc.set_relay(1, True)
    assert rc.get_cached(1) is True
    rc.disconnect()


def test_min_cycle_time_blocks_rapid_toggles():
    rc = make_controller()
    assert rc.set_relay(2, True) is True
    # Immediate second change is rejected
    assert rc.set_relay(2, False) is False
    assert rc.get_cached(2) is True
    rc.disconnect()


def test_all_off_bypasses_cycle_time():
    rc = make_controller()
    assert rc.set_relay(3, True) is True

    # Safety shutdown must win even though channel 3 changed <1s ago
    rc.all_off()

    assert all(not rc.get_cached(ch) for ch in range(1, 9))
    rc.disconnect()


def test_disconnect_turns_everything_off():
    rc = make_controller()
    rc.set_relay(4, True)
    rc.disconnect()
    assert not rc.get_cached(4)


def test_invalid_channel_rejected():
    rc = make_controller()
    assert rc.set_relay(9, True) is False
    assert rc.set_relay(0, True) is False
    rc.disconnect()
