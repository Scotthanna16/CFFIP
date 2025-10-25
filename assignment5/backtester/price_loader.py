import pandas as pd
import numpy as np


class PriceLoader:

    def generate_prices(
        self, n: int, start_price: float, mu: float, sigma: float, random=True
    ) -> pd.Series:

        if random == False:
            np.random.seed(0)

        returns = np.random.normal(mu, sigma, n)

        prices = start_price * np.exp(np.cumsum(returns))

        prices_list = prices.tolist()

        return pd.Series(prices_list, name="Prices")

