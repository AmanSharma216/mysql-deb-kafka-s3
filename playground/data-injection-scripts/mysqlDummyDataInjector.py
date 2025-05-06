import mysql.connector
from mysql.connector import Error
from faker import Faker
import random

host = 'localhost'
database = 'kafkaDB'
user = 'root'
password = 'amans21601'
port = 3307

fake = Faker()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        if connection.is_connected():
            print("Connection to MySQL database was successful")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def create_tables(connection):
    cursor = connection.cursor()

    tables = {
        "customers": """
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address VARCHAR(255),
                phone_number VARCHAR(50),  -- Increase size of the phone_number column
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """,
        "orders": """
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                product_id INT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                amount DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """,
        "products": """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
    }

    for table_name, create_table_sql in tables.items():
        try:
            cursor.execute(create_table_sql)
            print(f"Table {table_name} is ready or was created successfully.")
        except Error as e:
            print(f"Error creating table {table_name}: {e}")

    cursor.close()

def insert_dummy_data(connection, tables_to_insert):
    cursor = connection.cursor()

    def generate_customers_data(n):
        return [(fake.name(), fake.address(), fake.phone_number()) for _ in range(n)]

    def generate_products_data(n):
        return [(fake.word(), round(random.uniform(5, 200), 2)) for _ in range(n)]

    def generate_orders_data(n, customer_ids, product_ids):
        return [(random.choice(customer_ids), random.choice(product_ids), round(random.uniform(10, 500), 2)) for _ in range(n)]

    try:
        if 'customers' in tables_to_insert:
            customers_data = generate_customers_data(10)
            cursor.executemany("""
                INSERT INTO customers (name, address, phone_number) VALUES (%s, %s, %s)
            """, customers_data)
            print("Dummy data inserted into customers.")

        if 'products' in tables_to_insert:
            products_data = generate_products_data(10)
            cursor.executemany("""
                INSERT INTO products (name, price) VALUES (%s, %s)
            """, products_data)
            print("Dummy data inserted into products.")

        if 'orders' in tables_to_insert:
            cursor.execute("SELECT id FROM customers")
            customer_ids = [customer[0] for customer in cursor.fetchall()]
            cursor.execute("SELECT id FROM products")
            product_ids = [product[0] for product in cursor.fetchall()]
            orders_data = generate_orders_data(10, customer_ids, product_ids)
            cursor.executemany("""
                INSERT INTO orders (customer_id, product_id, amount) VALUES (%s, %s, %s)
            """, orders_data)
            print("Dummy data inserted into orders.")

        connection.commit()
        print("Dummy data insertion complete.")
    except Error as e:
        print(f"Error inserting dummy data: {e}")
    finally:
        cursor.close()

def choose_tables():
    chosen_tables = input("Enter the tables you want to insert random dummy data into (comma separated): ")
    return [table.strip() for table in chosen_tables.split(',')]

def main():
    connection = create_connection()

    if connection:
        create_tables(connection)

        tables_to_insert = choose_tables()

        insert_dummy_data(connection, tables_to_insert)

        connection.close()

if __name__ == "__main__":
    main()
