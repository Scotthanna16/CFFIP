# reporting.py
from .models import Instrument
from .analytics import VolatilityDecorator, BetaDecorator, DrawdownDecorator


def display_Instrument_analytics(Instrument, benchmark):
    return DrawdownDecorator(
        BetaDecorator(VolatilityDecorator(Instrument), benchmark)
    ).get_metrics()
