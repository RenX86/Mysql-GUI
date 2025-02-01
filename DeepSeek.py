import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error

class MySQLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MySQL GUI Client")
        
        # Connection variables
        self.connection = None
        self.host_var = tk.StringVar()
        self.user_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.database_var = tk.StringVar()

        self.create_connection_panel()
        self.create_query_panel()
        self.create_database_tree()
        self.create_result_panel()

    def create_connection_panel(self):
        # Connection Frame
        connection_frame = ttk.LabelFrame(self.root, text="Connection")
        connection_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Connection entries
        ttk.Label(connection_frame, text="Host:").grid(row=0, column=0, sticky="e")
        ttk.Entry(connection_frame, textvariable=self.host_var).grid(row=0, column=1)

        ttk.Label(connection_frame, text="User:").grid(row=1, column=0, sticky="e")
        ttk.Entry(connection_frame, textvariable=self.user_var).grid(row=1, column=1)

        ttk.Label(connection_frame, text="Password:").grid(row=2, column=0, sticky="e")
        ttk.Entry(connection_frame, textvariable=self.password_var, show="*").grid(row=2, column=1)

        ttk.Label(connection_frame, text="Database:").grid(row=3, column=0, sticky="e")
        ttk.Entry(connection_frame, textvariable=self.database_var).grid(row=3, column=1)

        # Connect button
        ttk.Button(connection_frame, text="Connect", command=self.connect).grid(row=4, column=1, pady=5)

    def create_query_panel(self):
        # Query Frame
        query_frame = ttk.LabelFrame(self.root, text="SQL Query")
        query_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Query input
        self.query_input = scrolledtext.ScrolledText(query_frame, width=60, height=8)
        self.query_input.grid(row=0, column=0, padx=5, pady=5)

        # Execute button
        ttk.Button(query_frame, text="Execute", command=self.execute_query).grid(row=1, column=0, pady=5)

    def create_database_tree(self):
        # Database Tree Frame
        tree_frame = ttk.LabelFrame(self.root, text="Database Structure")
        tree_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky="ns")

        # TreeView for databases and tables
        self.tree = ttk.Treeview(tree_frame)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Configure treeview columns
        self.tree["columns"] = ("type",)
        self.tree.heading("#0", text="Name")
        self.tree.heading("type", text="Type")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def create_result_panel(self):
        # Result Frame
        result_frame = ttk.LabelFrame(self.root, text="Results")
        result_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Result display using Treeview
        self.result_tree = ttk.Treeview(result_frame)
        self.result_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        y_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(result_frame, orient="horizontal", command=self.result_tree.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.result_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host_var.get(),
                user=self.user_var.get(),
                password=self.password_var.get(),
                database=self.database_var.get()
            )
            messagebox.showinfo("Success", "Connected to MySQL database!")
            self.populate_database_tree()
        except Error as err:
            messagebox.showerror("Error", f"Error connecting to MySQL: {err}")

    def populate_database_tree(self):
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        try:
            cursor = self.connection.cursor()
            
            # Get databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            for db in databases:
                db_name = db[0]
                db_node = self.tree.insert("", "end", text=db_name, values=("Database",))
                
                # Get tables for each database
                cursor.execute(f"SHOW TABLES FROM {db_name}")
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    self.tree.insert(db_node, "end", text=table_name, values=("Table",))
            
            cursor.close()
        except Error as err:
            messagebox.showerror("Error", f"Error fetching database structure: {err}")

    def execute_query(self):
        query = self.query_input.get("1.0", tk.END).strip()
        if not query:
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # For SELECT statements
            if cursor.description:
                results = cursor.fetchall()
                
                # Clear previous results
                self.result_tree.delete(*self.result_tree.get_children())
                
                # Create columns
                columns = [desc[0] for desc in cursor.description]
                self.result_tree["columns"] = columns
                for col in columns:
                    self.result_tree.heading(col, text=col)
                    self.result_tree.column(col, width=100)
                
                # Insert data
                for row in results:
                    self.result_tree.insert("", "end", values=row)
            else:
                self.connection.commit()
                messagebox.showinfo("Success", f"Query executed successfully. Rows affected: {cursor.rowcount}")
            
            cursor.close()
            self.populate_database_tree()  # Refresh database structure
        except Error as err:
            messagebox.showerror("Error", f"Error executing query: {err}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MySQLGUI(root)
    root.mainloop()