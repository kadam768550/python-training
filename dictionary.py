# Shop Inventory System using Dictionary

products = {
    101: {"name": "Laptop", "price": 50000, "stock": 10},
    102: {"name": "Mouse", "price": 500, "stock": 50},
    103: {"name": "Keyboard", "price": 1200, "stock": 30},
    104: {"name": "Monitor", "price": 10000, "stock": 15},
    105: {"name": "Printer", "price": 8000, "stock": 8}
}

sales = {
    101: 0,
    102: 0,
    103: 0,
    104: 0,
    105: 0
}

while True:
    print("\n========== SHOP INVENTORY SYSTEM ==========")
    print("1. Display All Products")
    print("2. Search Product by Name")
    print("3. Sell Product")
    print("4. Add Stock")
    print("5. View Sales Report")
    print("6. Total Inventory Value")
    print("7. Exit")

    choice = int(input("Enter your choice: "))

    if choice == 11:
        print("\nPRODUCT LIST")
        print("-" * 60)
        print("ID\tName\t\tPrice\tStock")
        print("-" * 60)

        for pid, info in products.items():
            print(pid, "\t", info["name"], "\t\t", info["price"], "\t", info["stock"])

    elif choice == 22:
        search_name = input("Enter product name to search: ").lower()

        found = False
        for pid, info in products.items():
            if info["name"].lower() == search_name:
                print("\nProduct Found")
                print("Product ID :", pid)
                print("Name       :", info["name"])
                print("Price      :", info["price"])
                print("Stock      :", info["stock"])
                found = True
                break

        if found == False:
            print("Product not found!")

    elif choice == 33:
        pid = int(input("Enter Product ID: "))

        if pid in products:
            qty = int(input("Enter quantity to sell: "))

            if qty <= products[pid]["stock"]:
                products[pid]["stock"] -= qty
                sales[pid] += qty

                bill = qty * products[pid]["price"]

                print("\nSale Successful")
                print("Product :", products[pid]["name"])
                print("Quantity:", qty)
                print("Bill Amount =", bill)

            else:
                print("Insufficient stock!")

        else:
            print("Invalid Product ID!")

    elif choice == 44:
        pid = int(input("Enter Product ID: "))

        if pid in products:
            qty = int(input("Enter quantity to add: "))
            products[pid]["stock"] += qty
            print("Stock updated successfully.")
        else:
            print("Invalid Product ID!")

    elif choice == 55:
        print("\nSALES REPORT")
        print("-" * 60)
        print("Product Name\tUnits Sold")
        print("-" * 60)

        total_sales_amount = 0

        for pid in products:
            amount = sales[pid] * products[pid]["price"]
            total_sales_amount += amount

            print(products[pid]["name"], "\t\t", sales[pid])

        print("-" * 60)
        print("Total Sales Amount =", total_sales_amount)

    elif choice == 66:
        total_value = 0

        for pid, info in products.items():
            total_value += info["price"] * info["stock"]

        print("Total Inventory Value =", total_value)

    elif choice == 77:
        print("Thank You for using Shop Inventory System.")
        break

    else:
        print("Invalid Choice! Please try again.")