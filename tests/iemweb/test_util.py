"""Test iemweb.util functions."""

import os
from pathlib import Path
from unittest.mock import patch

from iemweb.util import acquire_slot, month2months, release_slot


def test_slot_acquiring():
    """Test that we can acquire and release a slot."""
    res = acquire_slot("test", 1)
    assert res is not None
    release_slot(res)


def test_too_many_requests():
    """Test the failure."""
    res1 = acquire_slot("test", 1)
    assert res1 is not None
    res2 = acquire_slot("test", 1)
    assert res2 is None
    release_slot(res1)


def test_acquire_slot_creates_lock_directory():
    """Test that acquire_slot creates the lock directory if needed."""
    # Use a unique test name that doesn't exist yet
    test_name = f"test_create_dir_{os.getpid()}"

    # The function should create /tmp/test_create_dir_<pid>
    expected_dir = Path("/tmp") / test_name

    # Clean up if it exists from previous test
    if expected_dir.exists():
        import shutil

        shutil.rmtree(expected_dir)

    res = acquire_slot(test_name, 1)
    assert res is not None
    assert expected_dir.exists()
    release_slot(res)

    # Clean up
    import shutil

    shutil.rmtree(expected_dir)


def test_acquire_slot_multiple_processes():
    """Test acquiring multiple slots up to max_processes."""
    max_processes = 3
    slots = []

    # Acquire all available slots
    for _ in range(max_processes):
        slot = acquire_slot("test_multi", max_processes)
        assert slot is not None
        slots.append(slot)

    # Next attempt should fail
    slot = acquire_slot("test_multi", max_processes)
    assert slot is None

    # Release all slots
    for slot in slots:
        release_slot(slot)


def test_acquire_slot_osError_handling():
    """Test that OSError during file operations is handled correctly."""
    with patch("os.open") as mock_open:
        # First call succeeds, second call raises OSError
        mock_open.side_effect = [OSError("Permission denied"), 123]

        with patch("fcntl.flock"), patch("os.close"):
            # First slot should fail with OSError, second should succeed
            res = acquire_slot("test_error", 2)
            assert res == 123
            release_slot(res)


def test_acquire_slot_close_exception_handling():
    """Test that exceptions during os.close are handled gracefully."""
    with patch("os.open") as mock_open:
        mock_open.side_effect = OSError("File operation failed")

        with patch("os.close") as mock_close:
            # Make close raise an exception too
            mock_close.side_effect = Exception("Close failed")

            # Should not raise an exception, should try next slot
            res = acquire_slot("test_close_error", 1)
            assert res is None


def test_release_slot_with_none():
    """Test that release_slot handles None input gracefully."""
    # Should not raise an exception
    release_slot(None)


def test_release_slot_with_valid_fd():
    """Test normal release_slot operation."""
    res = acquire_slot("test_release", 1)
    assert res is not None

    # This should not raise an exception
    release_slot(res)


def test_release_slot_exception_handling():
    """Test that exceptions during release_slot are handled gracefully."""
    res = acquire_slot("test_release_error", 1)
    assert res is not None

    with patch("fcntl.flock") as mock_flock:
        mock_flock.side_effect = Exception("Unlock failed")

        # Should not raise an exception
        release_slot(res)


def test_release_slot_close_exception():
    """Test that exceptions during os.close in release_slot are handled."""
    res = acquire_slot("test_release_close_error", 1)
    assert res is not None

    with patch("os.close") as mock_close:
        mock_close.side_effect = Exception("Close failed")

        # Should not raise an exception
        release_slot(res)


def test_acquire_slot_all_busy_scenario():
    """Test scenario where all slots are busy and none can be acquired."""
    max_processes = 2

    # Acquire all available slots
    slot1 = acquire_slot("test_all_busy", max_processes)
    slot2 = acquire_slot("test_all_busy", max_processes)

    assert slot1 is not None
    assert slot2 is not None

    # Next attempt should return None
    slot3 = acquire_slot("test_all_busy", max_processes)
    assert slot3 is None

    # Release one slot
    release_slot(slot1)

    # Now we should be able to acquire again
    slot4 = acquire_slot("test_all_busy", max_processes)
    assert slot4 is not None

    # Clean up
    release_slot(slot2)
    release_slot(slot4)


def test_str_case():
    """Test our month2months function."""
    assert month2months("Jan") == [1]
    assert month2months("jan") == [1]
    assert month2months("JAN") == [1]
    assert month2months(" 01 ") == [1]
