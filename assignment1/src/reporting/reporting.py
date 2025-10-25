import csv
import math
import matplotlib.pyplot as plt


RISK_FREE_RATE = 0.04  # Annual risk-free rate


class Report:
    def __init__(self):
        self.__logs = []
        self.__trades = [["Action", "Symbol", "Quantity", "Price", "Status"]]
        # portfolio history will store dictionaries suitable for csv.DictWriter
        self.__portfolio_history = []
        # numeric history for performance calculations (list of floats)
        self.__equity_curve = []

    def add_trade_log(self, trade=None, log=None):
        # If trade successful
        if trade:
            self.__trades.append(
                [trade.action, trade.symbol, trade.quantity, trade.price, trade.status]
            )
            log = f"{trade.action} {trade.quantity} of {trade.symbol} at price {trade.price}. Order status is {trade.status}"
            self.__logs.append(log)

        # Trade not successful
        else:
            # In this case log would be the error message
            self.__logs.append(log)

    def execute_trade(self, trade, log, portfolio):
        self.add_trade_log(trade, log)

        # store human-readable portfolio snapshot for CSV output
        self.__portfolio_history.append(portfolio.positions)

        # attempt to store a numeric snapshot for performance calculations
        try:
            snap = portfolio.snapshot()
            # compute a simple equity value: cash + sum(quantity * avg_price)
            equity = float(snap.get("Cash", 0.0))
            for symbol, info in snap.items():
                if symbol == "Cash":
                    continue
                qty = info.get("quantity", 0)
                avg = info.get("avg_price", 0.0)
                equity += float(qty) * float(avg)

            self.__equity_curve.append(equity)
        except Exception:
            # if portfolio doesn't implement snapshot we'll skip numeric history
            self.__equity_curve.append(None)

    @property
    def portfolio_history(self):
        return self.__portfolio_history

    @property
    def logs(self):
        return self.__logs

    def display_logs(self):
        for log in self.__logs:
            print(log)

    def create_portfolio_data(self):

        fieldnames = self.__portfolio_history[-1].keys()
        with open("out/portfolio_data.csv", "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.__portfolio_history)

    def create_trade_data(self):
        with open("out/trade_data.csv", "w", newline="") as csvfile:

            writer = csv.writer(csvfile)
            writer.writerows(self.__trades)

    def create_performance_data(self):
        # filter out None entries
        equity = [e for e in self.__equity_curve if e is not None]
        if not equity:
            # nothing to compute
            return

        # write equity curve
        with open("out/equity_curve.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["equity"])
            for v in equity:
                writer.writerow([v])

        returns = []
        for i in range(1, len(equity)):
            prev = equity[i - 1]
            cur = equity[i]
            if prev == 0:
                returns.append(0.0)
            else:
                returns.append((cur - prev) / prev)

        avg_ret = sum(returns) / len(returns) if returns else 0.0
        std_ret = (
            math.sqrt(sum((r - avg_ret) ** 2 for r in returns) / len(returns))
            if returns
            else 0.0
        )
        sharpe = (
            (avg_ret - RISK_FREE_RATE / 252) / (std_ret) * math.sqrt(252)
            if std_ret > 0
            else 0.0
        )

        # max drawdown
        peak = equity[0]
        max_dd = 0.0
        for v in equity:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak != 0 else 0.0
            if dd > max_dd:
                max_dd = dd

        total_return = (equity[-1] - equity[0]) / equity[0] if equity[0] != 0 else 0.0

        with open("performance.md", "w") as f:
            f.write("# Performance Summary\n\n")
            f.write(f"Total Return: {total_return:.4f}\n\n")
            f.write(f"Sharpe Ratio (annualized): {sharpe:.4f}\n\n")
            f.write(f"Max Drawdown: {max_dd:.4f}\n\n")
            f.write("Equity curve is saved in `out/equity_curve.csv`.\n")

        with open("out/periodic_returns.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["return"])
            for r in returns:
                writer.writerow([r])

    def _generate_narrative(
        self, total_return, average_return, std_return, annual_sharpe, max_drawdown
    ):
        """
        Generate a short narrative of the performance of the strategy.
        """
        # Performance characterization
        if total_return > 0.0:
            perf_word = "positive"
        elif total_return < 0.0:
            perf_word = "negative"
        else:
            perf_word = "flat"

        # Sharpe interpretation
        if annual_sharpe >= 1.0:
            sharpe_word = "favorable risk-adjusted performance"
        elif annual_sharpe > 0.0:
            sharpe_word = "marginal risk-adjusted performance"
        else:
            sharpe_word = "underperformance versus the risk-free rate"

        # Drawdown interpretation
        dd = abs(max_drawdown)
        if dd >= 0.20:
            dd_word = "severe"
        elif dd >= 0.10:
            dd_word = "moderate"
        else:
            dd_word = "mild"

        # Volatility characterization (daily sigma)
        daily_sigma = std_return
        if daily_sigma >= 0.02:
            vol_word = "very high"
        elif daily_sigma >= 0.01:
            vol_word = "high"
        elif daily_sigma >= 0.005:
            vol_word = "moderate"
        else:
            vol_word = "low"

        # Overall verdict
        if total_return > 0 and annual_sharpe >= 1.0 and dd < 0.20:
            verdict = "Potentially Good Strategy"
        elif annual_sharpe <= 0 or total_return <= 0:
            verdict = "Potentially Bad Strategy"
        else:
            verdict = "Mixed Results"

        narrative_lines = [
            f"The strategy delivered a {perf_word} total return of {total_return:.2%} with an annualized Sharpe of {annual_sharpe:.2f}, indicating {sharpe_word}.",
            f"Risk was {dd_word} with a maximum drawdown of {max_drawdown:.2%}.",
            f"Periodic return volatility appears {vol_word} (daily vol approximately {daily_sigma:.2%}).",
            "Overall verdict: " + verdict,
        ]

        return "\n".join(narrative_lines)

    def performance_report(self):
        """
        Generate a performance report.

            Total return
            Series of periodic returns
            Sharpe ratio
            Maximum drawdown
        """
        total_return = (
            self.__equity_curve[-1] - self.__equity_curve[0]
        ) / self.__equity_curve[0]

        returns = [
            (self.__equity_curve[i] - self.__equity_curve[i - 1])
            / self.__equity_curve[i - 1]
            for i in range(1, len(self.__equity_curve))
        ]

        average_return = sum(returns) / len(returns)

        std_return = math.sqrt(
            sum((r - average_return) ** 2 for r in returns) / len(returns)
        )

        daily_sharpe = (average_return - RISK_FREE_RATE / 252) / std_return
        annual_sharpe = daily_sharpe * math.sqrt(252)

        # max drawdown
        max_drawdown = min(
            (self.__equity_curve[i] - self.__equity_curve[j]) / self.__equity_curve[j]
            for i in range(len(self.__equity_curve))
            for j in range(i)
        )

        # create equity curve plot
        fig, ax = plt.subplots()
        ax.plot(self.__equity_curve)

        ax.set_xlabel("Time")
        ax.set_ylabel("Equity")
        ax.set_title("Equity Curve")
        ax.legend()
        fig.autofmt_xdate()

        fig.savefig("out/equity_curve.png")

        # create periodic returns plot
        fig, ax = plt.subplots()
        ax.hist(returns, bins=30)
        ax.set_xlabel("Return")
        ax.set_ylabel("Frequency")
        ax.set_title("Periodic Returns")
        fig.savefig("out/periodic_returns.png")
        narrative = self._generate_narrative(
            total_return=total_return,
            average_return=average_return,
            std_return=std_return,
            annual_sharpe=annual_sharpe,
            max_drawdown=max_drawdown,
        )

        report = f"""# Performance Report

## Summary of Performance Metrics

| Metric                                 | Value    |
| -------------------------------------- | -------- |
| Total Return                           | {total_return:.4f}  |
| Mean Periodic Return                   | {average_return:.4f}  |
| Standard Deviation of Periodic Returns | {std_return:.4f}   |
| Annualized Sharpe ratio                | {annual_sharpe:.4f} |
| Maximum drawdown                       | {max_drawdown:.4f}   |

## Narrative Interpretation

{narrative}

## Equity Curve Plot

![Equity Curve](./out/equity_curve.png 'equity curve at out/equity_curve.png')

## Periodic Returns Plot

![Periodic Returns](./out/periodic_returns.png 'periodic returns at out/periodic_returns.png')
"""
        return report

    def output_performance_report(self):
        with open("performance.md", "w") as f:
            f.write(self.performance_report())
