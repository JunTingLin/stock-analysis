from finlab import data
from finlab.backtest import sim

close = data.get('price:收盤價')
pb = data.get('price_earning_ratio:股價淨值比')  

sma20 = close.average(20)
sma60 = close.average(60)

entries = close > sma20
exits = close < sma60

position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)
sim(position)