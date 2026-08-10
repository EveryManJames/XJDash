"""Tests for skin loading and the change-notification observer."""
import os

from skins.skin_manager import SkinManager


def make_manager(repo_root):
    return SkinManager(skins_dir=os.path.join(repo_root, 'skins'))


def test_load_and_colors(repo_root):
    sm = make_manager(repo_root)
    assert sm.load_skin('default_amber')
    assert sm.get_color('primary') == (255, 176, 0)
    # Missing color falls back to default
    assert sm.get_color('nope', default=(1, 2, 3)) == (1, 2, 3)


def test_missing_skin_fails_gracefully(repo_root):
    sm = make_manager(repo_root)
    assert sm.load_skin('does_not_exist') is False


def test_list_available_skins(repo_root):
    sm = make_manager(repo_root)
    skins = sm.list_available_skins()
    assert 'default_amber' in skins
    assert 'green_vfd' in skins


def test_subscribers_notified_on_load(repo_root):
    sm = make_manager(repo_root)
    calls = []
    sm.subscribe(lambda: calls.append(sm.current_skin))

    sm.load_skin('default_amber')
    sm.load_skin('green_vfd')
    sm.load_skin('does_not_exist')  # failed load: no notification

    assert calls == ['default_amber', 'green_vfd']


def test_broken_subscriber_does_not_break_load(repo_root):
    sm = make_manager(repo_root)

    def bad_listener():
        raise RuntimeError('boom')

    ok_calls = []
    sm.subscribe(bad_listener)
    sm.subscribe(lambda: ok_calls.append(1))

    assert sm.load_skin('default_amber') is True
    assert ok_calls == [1]
