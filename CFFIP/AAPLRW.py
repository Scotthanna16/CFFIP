import yfinance as yf
import pandas as pd
import numpy as np


data = yf.download("AAPL", start="2008-01-01", end="2025-01-01")
AAPLdf = pd.DataFrame(data)
AAPLdf["Signal"] = np.random.randint(0, 2, AAPLdf.shape[0])
AAPLdf["Action"] = AAPLdf["Signal"].diff()
AAPLdf = AAPLdf.dropna()
AAPLdf["Cash"] = 10000
AAPLdf["Cash"] = AAPLdf["Cash"]
print(AAPLdf)
