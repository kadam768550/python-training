# Shop Inventory System

products = ["Pen", "Book", "Pencil"]
stocks = [100, 50, 80]
sales = [20, 10, 15]

print("SHOP INVENTORY")
print("Product\tStock\tSales")

for i in range(len(products)):
    print(products[i], "\t", stocks[i], "\t", sales[i])

# Add a new product
p = input("\nEnter new product: ")
s = int(input("Enter stock quantity: "))
sl = int(input("Enter sales quantity: "))

products.append(p)
stocks.append(s)
sales.append(sl)

print("\nUPDATED INVENTORY")
print("Product\tStock\tSales")

for i in range(len(products)):
    print(products[i], "\t", stocks[i], "\t", sales[i])