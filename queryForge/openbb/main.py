from openbb import obb

# Fetch historical stock data for Apple
result = obb.equity.price.historical("AAPL")

# Convert the result to a DataFrame and print
df = result.to_dataframe()
print(df.head())