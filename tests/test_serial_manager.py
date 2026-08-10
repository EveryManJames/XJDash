"""Tests for REM line parsing and the mock serial source."""
from core.serial_manager import SerialManager
from core.mock_serial import MockREMSerial


def make_manager(fresh_data_manager):
    return SerialManager(fresh_data_manager)


def test_mock_line_parses_cleanly(fresh_data_manager):
    sm = make_manager(fresh_data_manager)
    line = MockREMSerial().read_line()

    data = sm._parse_line(line)

    assert data is not None
    assert set(data.keys()) == set(SerialManager.FIELD_NAMES)
    # Numeric fields parse as numbers, string fields stay strings
    assert isinstance(data['RPM'], float)
    assert 600 <= data['RPM'] <= 2500
    assert data['Loop'] in ('OPEN', 'CLSD')
    assert data['Sync'] == '+'


def test_wrong_field_count_rejected(fresh_data_manager):
    sm = make_manager(fresh_data_manager)
    assert sm._parse_line('1 2 3') is None
    assert sm._parse_line('') is None


def test_garbage_numeric_field_becomes_zero(fresh_data_manager):
    sm = make_manager(fresh_data_manager)
    good = MockREMSerial().read_line()
    values = good.split()
    values[5] = 'garbage'  # RPM position

    data = sm._parse_line(' '.join(values))

    assert data is not None
    assert data['RPM'] == 0
