import sqlite3

conn = sqlite3.connect("myproject.db")
cursor = conn.cursor()

cursor.execute("""
DELETE FROM categories
WHERE name IN ('Laptops','Mobiles')
""")
conn.commit()

print("Laptops and Mobiles categories deleted successfully.")

conn.close()