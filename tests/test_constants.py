import pytest
from chemios import StatusCodes as codes


def test_idle():
    expected = "100 Idle"
    assert expected == codes.idle()


@pytest.mark.parametrize('text', ['Waiting to Start'])
def test_idle_text(text):
    expected = "{} {} - {}".format(100, "Idle", text)
    assert expected == codes.idle(text)


def test_running():
    expected = "200 Running"
    assert expected == codes.running()


@pytest.mark.parametrize('text', ['Going'])
def test_running_text(text):
    expected = "{} {} - {}".format(200, "Running", text)
    assert expected == codes.running(text)


def test_stopped():
    expected = "300 Stopped"
    assert expected == codes.stopped()


@pytest.mark.parametrize('text', ['Error with device'])
def test_stopped_text(text):
    expected = "{} {} - {}".format(300, "Stopped", text)
    assert expected == codes.stopped(text)
