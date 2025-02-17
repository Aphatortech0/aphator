import pandas as pd
import numpy as np
import logging

class Backtester:
    def __init__(self):
        self.initial_capital = 10000
        self.position = 0
        self.portfolio_value = []

    def run_backtest(self, df, signals):
        try:
            if df.empty or signals.empty:
                logging.warning("Empty data provided for backtesting")
                return {
                    'Total Return': 0.0,
                    'Win Rate': 0.0,
                    'Max Drawdown': 0.0,
                    'Number of Trades': 0
                }

            capital = self.initial_capital
            position = 0
            trades = []
            self.portfolio_value = [capital]  # Initialize with starting capital

            for idx, row in signals.iterrows():
                try:
                    price = df.loc[idx, 'close']

                    if row['Final_Signal'] == 'BUY' and position == 0:
                        position = capital / price
                        trades.append({
                            'type': 'BUY',
                            'price': price,
                            'position': position,
                            'date': idx
                        })
                    elif row['Final_Signal'] == 'SELL' and position > 0:
                        capital = position * price
                        position = 0
                        trades.append({
                            'type': 'SELL',
                            'price': price,
                            'capital': capital,
                            'date': idx
                        })

                    current_value = capital if position == 0 else position * price
                    self.portfolio_value.append(current_value)
                except KeyError:
                    continue

            # Calculate performance metrics safely
            if len(self.portfolio_value) > 1:
                returns = np.array(self.portfolio_value) / self.initial_capital - 1
                total_return = returns[-1] * 100

                # Calculate win rate
                profitable_trades = 0
                trade_pairs = len(trades) // 2

                if trade_pairs > 0:
                    for i in range(0, len(trades)-1, 2):
                        if i+1 < len(trades):
                            buy_trade = trades[i]
                            sell_trade = trades[i+1]
                            if sell_trade['capital'] > buy_trade['position'] * buy_trade['price']:
                                profitable_trades += 1

                    win_rate = profitable_trades / trade_pairs
                else:
                    win_rate = 0.0

                # Calculate maximum drawdown
                peak = np.maximum.accumulate(self.portfolio_value)
                drawdown = (peak - self.portfolio_value) / np.where(peak == 0, 1, peak)
                max_drawdown = np.max(drawdown) * 100 if len(drawdown) > 0 else 0.0

            else:
                total_return = 0.0
                win_rate = 0.0
                max_drawdown = 0.0

            return {
                'Total Return': total_return,
                'Win Rate': win_rate,
                'Max Drawdown': max_drawdown,
                'Number of Trades': len(trades)
            }

        except Exception as e:
            logging.error(f"Error in backtesting: {str(e)}")
            return {
                'Total Return': 0.0,
                'Win Rate': 0.0,
                'Max Drawdown': 0.0,
                'Number of Trades': 0
            }