import sqlite3

conn = sqlite3.connect("myproject.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM categories")
conn.commit()

print("All categories deleted successfully.")

conn.close()