from src.patterns.singleton import Config


def test_singleton_behavior():
    cfg1 = Config()
    cfg2 = Config()
    assert cfg1 is cfg2
