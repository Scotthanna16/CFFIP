from src.patterns.strategy import MeanReversionStrategy, BreakoutStrategy


def test_mean_reversion_strategy_from_json(strategy_params):
    strategy = MeanReversionStrategy.from_json("jsons/strategy_params.json")
    assert isinstance(strategy, MeanReversionStrategy)
    assert (
        strategy._lookback_window
        == strategy_params["MeanReversionStrategy"]["lookback_window"]
    )
    assert strategy._threshold == strategy_params["MeanReversionStrategy"]["threshold"]


def test_mean_reversion_signal_generation(mean_reversion_strategy, sample_market_data):
    strategy = mean_reversion_strategy
    data_points = sample_market_data

    signals = []
    for point in data_points:
        signal = strategy.generate_signals(point)
        signals.append((point.price, signal))

    # Check that signals are generated correctly
    # First 20 points should have no signals due to lookback window
    for price, signal in signals[:20]:
        assert signal == []

    # The last point should generate a SELL signal since price jumps to 200
    assert signals[-1][1] == ["SELL"]


def test_breakout_strategy_from_json(breakout_strategy_params):

    strategy = BreakoutStrategy.from_json("jsons/strategy_params.json")
    assert isinstance(strategy, BreakoutStrategy)
    assert strategy._lookback_window == breakout_strategy_params["lookback_window"]
    assert strategy._threshold == breakout_strategy_params["threshold"]


def test_breakout_signal_generation(breakout_strategy, sample_market_data):

    strategy = breakout_strategy
    data_points = sample_market_data

    signals = []
    for point in data_points:
        signal = strategy.generate_signals(point)
        signals.append((point.price, signal))

    # Check that signals are generated correctly
    # First 20 points should have no signals due to lookback window
    for price, signal in signals[:20]:
        assert signal == []

    # The last point should generate a BUY signal since price jumps to 200
    assert signals[-1][1] == ["BUY"]
