import pandas as pd

RAW = r"C:\Users\mayank\OneDrive\Desktop\Project-FORESIGHT\Data\raw"

sales = pd.read_csv(RAW + "\\bm_sales.csv", usecols=["sku_id"])
inventory = pd.read_csv(RAW + "\\bm_inventory.csv", usecols=["sku_id"])

print("sales rows:", len(sales), "unique sku_id:", sales.sku_id.nunique())
print("inventory rows:", len(inventory), "unique sku_id:", inventory.sku_id.nunique())
print("inventory duplicate rows:", len(inventory) - inventory.sku_id.nunique())

# check if sales sku_id is unique
print("sales duplicate rows:", len(sales) - sales.sku_id.nunique())

# duplicate sku ids in inventory
print("\nTop duplicated sku_id in inventory (count):")
print(inventory.sku_id.value_counts().head(10))

# columns of full inventory
inv_full = pd.read_csv(RAW + "\\bm_inventory.csv", nrows=3)
print("\nInventory columns:", list(inv_full.columns))
