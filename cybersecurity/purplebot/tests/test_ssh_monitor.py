from pathlib import Path

import pytest

import ssh_monitor

FIXTURE = Path(__file__).parent / "fixtures" / "auth.log"


@pytest.fixture
def data():
    return ssh_monitor.analyze_ssh_log(FIXTURE)


@pytest.fixture
def config(tmp_path):
    return ssh_monitor.load_config(env_file=tmp_path / "missing.env", environ={"ENABLE_GEOIP": "false"})


def test_counts_failed_attempts_per_source(data):
    assert data["total_failed"] == 8
    assert data["failed"]["root@203.0.113.10"] == 5
    assert data["failed"]["admin@198.51.100.7"] == 2
    assert data["ips"] == {"203.0.113.10": 5, "198.51.100.7": 3}


def test_invalid_user_prefix_is_not_part_of_username(data):
    assert "admin" in data["users"]
    assert not any(user.startswith("invalid") for user in data["users"])


def test_tracks_first_and_last_seen(data):
    assert data["first_seen"]["root@203.0.113.10"] == "Sep 14 15:01:02"
    assert data["last_seen"]["root@203.0.113.10"] == "Sep 14 15:01:15"


def test_successful_login_is_recorded(data):
    assert data["successful"] == [{"time": "Sep 14 15:10:00", "user": "rezzodan", "ip": "192.168.0.50"}]


def test_threshold_marks_only_noisy_sources(data):
    assert ssh_monitor.suspicious_sources(data, threshold=5) == {"root@203.0.113.10": 5}


def test_unrelated_lines_are_ignored():
    result = ssh_monitor.parse_log_lines(["Sep 14 15:12:00 kali CRON[1]: session opened for user root"])
    assert result["total_failed"] == 0
    assert result["successful"] == []


def test_missing_log_returns_none(tmp_path):
    assert ssh_monitor.analyze_ssh_log(tmp_path / "nope.log") is None


def test_telegram_message_escapes_html_from_log(data, config):
    msg = ssh_monitor.build_telegram_message(data, config)
    assert "<b>x</b>" not in msg
    assert "&lt;b&gt;x&lt;/b&gt;" in msg


def test_no_message_without_failed_attempts(config):
    empty = ssh_monitor.parse_log_lines([])
    assert ssh_monitor.build_telegram_message(empty, config) is None


def test_private_ips_are_not_sent_to_geoip(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("GeoIP API must not be called for private addresses")

    monkeypatch.setattr(ssh_monitor.requests, "get", fail)
    assert ssh_monitor.get_country("192.168.0.50") == "Private network"
    assert ssh_monitor.get_country("not-an-ip") == "Unknown"


def test_config_reads_env_file_and_environment_wins(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_TOKEN=123:abc\nTELEGRAM_CHAT_ID=42\nTHRESHOLD=3\n# comment\n", encoding="utf-8")

    config = ssh_monitor.load_config(env_file=env_file, environ={"THRESHOLD": "7"})

    assert config["telegram_enabled"] is True
    assert config["threshold"] == 7
    assert config["log_file"] == "/var/log/auth.log"


def test_placeholder_token_disables_telegram(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN\nTELEGRAM_CHAT_ID=YOUR_CHAT_ID\n", encoding="utf-8")
    config = ssh_monitor.load_config(env_file=env_file, environ={})

    def fail(*args, **kwargs):
        raise AssertionError("Telegram API must not be called without a real token")

    monkeypatch.setattr(ssh_monitor.requests, "post", fail)
    assert config["telegram_enabled"] is False
    assert ssh_monitor.send_telegram("hi", config) is False
