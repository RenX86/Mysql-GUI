import tkinter as tk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import logging
import os, json
from tkinter import simpledialog, messagebox

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

class MySQLAdvancedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced MySQL GUI")
        self.root.geometry("1200x700")
        
        # Initialize database credentials
        self.db_params = {}
        self.current_database = None
        self.load_config()

        # Create main frame
        self.main_frame = ttkb.Frame(self.root, padding=20)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create notebook for tabs
        self.notebook = ttkb.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        # Create menu bar
        self.menu_bar = ttkb.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.create_menu()

        # Check if credentials are loaded
        if not self.db_params:
            self.show_login_dialog()
        else:
            self.connect_to_db()
            self.create_table_tabs()
            self.create_database_management_frame()
            self.create_cli_tab()

    def load_config(self):
        """Load database credentials from a config file."""
        config_file = "db_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    self.db_params = json.load(f)
                    logging.info("Loaded database configuration from file.")
            except json.JSONDecodeError:
                logging.warning("Invalid JSON format in config file.")
                self.db_params = {}

    def save_config(self):
        """Save database credentials to a config file."""
        config_file = "db_config.json"
        try:
            with open(config_file, "w") as f:
                json.dump(self.db_params, f)
                logging.info("Saved database configuration to file.")
        except IOError:
            logging.error("Failed to save database configuration.")

    def show_login_dialog(self):
        """Show a login dialog to enter database credentials."""
        login_window = tk.Toplevel(self.root)
        login_window.title("Database Login")
        login_window.geometry("400x300")

        # Input fields
        tk.Label(login_window, text="Host:").grid(row=0, column=0, padx=5, pady=5)
        host_entry = tk.Entry(login_window)
        host_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(login_window, text="User:").grid(row=1, column=0, padx=5, pady=5)
        user_entry = tk.Entry(login_window)
        user_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(login_window, text="Password:").grid(row=2, column=0, padx=5, pady=5)
        password_entry = tk.Entry(login_window, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(login_window, text="Database:").grid(row=3, column=0, padx=5, pady=5)
        database_entry = tk.Entry(login_window)
        database_entry.grid(row=3, column=1, padx=5, pady=5)

        # Submit button
        def submit():
            self.db_params = {
                "host": host_entry.get(),
                "user": user_entry.get(),
                "password": password_entry.get(),
                "database": database_entry.get()
            }
            self.save_config()
            login_window.destroy()
            self.connect_to_db()
            self.create_table_tabs()

        submit_btn = tk.Button(login_window, text="Connect", command=submit)
        submit_btn.grid(row=4, column=0, columnspan=2, pady=10)

    def connect_to_db(self):
        """Connect to MySQL database using dynamic credentials"""
        try:
            self.connection = mysql.connector.connect(**self.db_params)
            logging.info("Database connection successful")
        except Error as e:
            logging.error(f"Database connection failed: {e}")

    def create_menu(self):
        """Create application menu"""
        db_menu = ttkb.Menu(self.menu_bar, tearoff=0)
        db_menu.add_command(label="Connect", command=self.show_login_dialog)
        db_menu.add_command(label="Disconnect", command=self.disconnect_db)
        db_menu.add_command(label="Create Database...", command=lambda: self.create_database())
        db_menu.add_command(label="Switch Database...", command=lambda: self.switch_database())
        self.menu_bar.add_cascade(label="Database", menu=db_menu)

        table_menu = ttkb.Menu(self.menu_bar, tearoff=0)
        table_menu.add_command(label="Create Table...", command=lambda: self.create_table())
        table_menu.add_command(label="Edit Table...", command=lambda: self.edit_table())
        self.menu_bar.add_cascade(label="Table", menu=table_menu)

        column_menu = ttkb.Menu(self.menu_bar, tearoff=0)
        column_menu.add_command(label="Add Column...", command=lambda: self.add_column())
        column_menu.add_command(label="Modify Column...", command=lambda: self.modify_column())
        column_menu.add_command(label="Drop Column...", command=lambda: self.drop_column())
        self.menu_bar.add_cascade(label="Columns", menu=column_menu)

    def create_database(self):
        """Create a new database"""
        db_name = simpledialog.askstring("Create Database", "Enter database name:")
        if db_name:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE {db_name}")
                self.connection.commit()
                logging.info(f"Database {db_name} created")
                messagebox.showinfo("Success", f"Database {db_name} created successfully")
                cursor.close()
            except Error as e:
                logging.error(f"Error creating database: {e}")
                messagebox.showerror("Error", f"Failed to create database: {e}")

    def switch_database(self):
        """Switch to a different database"""
        db_name = simpledialog.askstring("Switch Database", "Enter database name:")
        if db_name:
            try:
                self.connection = mysql.connector.connect(
                    host=self.db_params['host'],
                    user=self.db_params['user'],
                    password=self.db_params['password'],
                    database=db_name
                )
                self.db_params['database'] = db_name
                self.save_config()
                logging.info(f"Switched to database {db_name}")
                self.notebook.destroy()
                self.notebook = ttkb.Notebook(self.main_frame)
                self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
                self.create_table_tabs()
                self.create_database_management_frame()
                self.create_cli_tab()
                messagebox.showinfo("Success", f"Switched to database {db_name}")
            except Error as e:
                logging.error(f"Error switching database: {e}")
                messagebox.showerror("Error", f"Failed to switch to database: {e}")

    def create_table(self):
        """Create a new table"""
        table_name = simpledialog.askstring("Create Table", "Enter table name:")
        if table_name:
            columns = None
            while not columns:
                columns = simpledialog.askstring("Table Columns", 
                    "Enter comma-separated column definitions (e.g., col1 INT, col2 VARCHAR(100))")
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE TABLE {table_name} ({columns})")
                self.connection.commit()
                logging.info(f"Table {table_name} created")
                messagebox.showinfo("Success", f"Table {table_name} created successfully")
                self.notebook.destroy()
                self.notebook = ttkb.Notebook(self.main_frame)
                self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
                self.create_table_tabs()
                self.create_database_management_frame()
                self.create_cli_tab()
                cursor.close()
            except Error as e:
                logging.error(f"Error creating table: {e}")
                messagebox.showerror("Error", f"Failed to create table: {e}")

    def add_column(self):
        """Add a new column to an existing table"""
        table_name = self.get_selected_table()
        if not table_name:
            return
        column_def = simpledialog.askstring("Add Column", "Enter column definition (e.g., new_col INT):")
        if column_def:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_def}")
                self.connection.commit()
                logging.info(f"Column {column_def} added to {table_name}")
                messagebox.showinfo("Success", f"Column {column_def} added to {table_name} successfully")
                self.refresh_data(table_name)
                cursor.close()
            except Error as e:
                logging.error(f"Error adding column: {e}")
                messagebox.showerror("Error", f"Failed to add column: {e}")

    def modify_column(self):
        """Modify an existing column"""
        table_name = self.get_selected_table()
        if not table_name:
            return
        column_def = simpledialog.askstring("Modify Column", 
            "Enter modified column definition (e.g., col_name INT NOT NULL):")
        if column_def:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"ALTER TABLE {table_name} MODIFY COLUMN {column_def}")
                self.connection.commit()
                logging.info(f"Column {column_def} modified in {table_name}")
                messagebox.showinfo("Success", f"Column {column_def} modified in {table_name} successfully")
                self.refresh_data(table_name)
                cursor.close()
            except Error as e:
                logging.error(f"Error modifying column: {e}")
                messagebox.showerror("Error", f"Failed to modify column: {e}")

    def drop_column(self):
        """Drop a column from a table"""
        table_name = self.get_selected_table()
        if not table_name:
            return
        column_name = simpledialog.askstring("Drop Column", "Enter column name to drop:")
        if column_name:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                self.connection.commit()
                logging.info(f"Column {column_name} dropped from {table_name}")
                messagebox.showinfo("Success", f"Column {column_name} dropped from {table_name} successfully")
                self.refresh_data(table_name)
                cursor.close()
            except Error as e:
                logging.error(f"Error dropping column: {e}")
                messagebox.showerror("Error", f"Failed to drop column: {e}")

    def get_selected_table(self):
        """Get the selected table name from the current tab"""
        current_tab = self.notebook.select()
        if current_tab:
            tab_idx = self.notebook.index(current_tab)
            if tab_idx >= 0:
                return self.notebook.tab(tab_idx, "text")
        messagebox.showerror("Error", "No table selected")
        return None

    def create_database_management_frame(self):
        """Create a frame for database management operations"""
        db_frame = ttkb.Frame(self.main_frame, padding=10)
        self.notebook.add(db_frame, text="Database Management")

        # Create Database Button
        create_db_btn = ttkb.Button(db_frame, text="Create Database", command=self.create_database)
        create_db_btn.grid(row=0, column=0, padx=5, pady=5)

        # Switch Database Button
        switch_db_btn = ttkb.Button(db_frame, text="Switch Database", command=self.switch_database)
        switch_db_btn.grid(row=0, column=1, padx=5, pady=5)

        # Current Database Label
        current_db_label = ttkb.Label(db_frame, text=f"Current Database: {self.db_params.get('database', 'N/A')}")
        current_db_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def create_cli_tab(self):
        """Create a tab for running raw SQL commands"""
        cli_frame = ttkb.Frame(self.main_frame, padding=10)
        self.notebook.add(cli_frame, text="CLI")

        # Command Entry
        self.cli_entry = ttkb.Entry(cli_frame)
        self.cli_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        # Execute Button
        execute_btn = ttkb.Button(cli_frame, text="Execute", command=self.execute_cli_command)
        execute_btn.grid(row=0, column=1, padx=5, pady=5)

        # Output Text Area
        self.cli_output = ttkb.Text(cli_frame, height=10, width=50)
        self.cli_output.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        cli_frame.columnconfigure(0, weight=1)
        cli_frame.rowconfigure(1, weight=1)

    def execute_cli_command(self):
        """Execute the entered SQL command"""
        command = self.cli_entry.get()
        if command:
            try:
                cursor = self.connection.cursor()
                cursor.execute(command)
                if command.strip().upper().startswith(("SELECT", "SHOW")):
                    result = cursor.fetchall()
                    self.cli_output.delete('1.0', tk.END)
                    self.cli_output.insert(tk.END, str(result))
                else:
                    self.connection.commit()
                    self.cli_output.delete('1.0', tk.END)
                    self.cli_output.insert(tk.END, f"Command executed successfully: {command}")
                logging.info(f"Executed CLI command: {command}")
            except Error as e:
                logging.error(f"Error executing command: {e}")
                self.cli_output.delete('1.0', tk.END)
                self.cli_output.insert(tk.END, f"Error: {e}")
            finally:
                cursor.close()

    def refresh_data(self, table_name=None):
        """Refresh the data grid for all or specific tables"""
        if table_name:
            current_tab = self.notebook.index("current")
            if current_tab >= 0:
                tab_frame = self.notebook.nametowidget(self.notebook.tabs()[current_tab])
                for child in tab_frame.winfo_children():
                    if isinstance(child, ttkb.Treeview):
                        for item in child.get_children():
                            child.delete(item)
                        self.load_table_data(table_name, child['columns'])
                        break
        else:
            for tab in self.notebook.tabs():
                tab_frame = self.notebook.nametowidget(tab)
                for child in tab_frame.winfo_children():
                    if isinstance(child, ttkb.Treeview):
                        for item in child.get_children():
                            child.delete(item)
                        table_name = self.notebook.tab(tab, 'text')
                        self.load_table_data(table_name, child['columns'])
                                    
    def disconnect_db(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")

    def create_table_tabs(self):
        """Create tabs for each table in the database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                tab_frame = ttkb.Frame(self.notebook)
                self.notebook.add(tab_frame, text=table_name)
                
                self.create_table_ui(table_name, tab_frame)

            cursor.close()
        except Error as e:
            logging.error(f"Error fetching tables: {e}")

    def create_table_ui(self, table_name, parent):
        """Create UI elements for a specific table"""
        # Create table schema
        schema_frame = ttkb.Frame(parent, padding=10)
        schema_frame.grid(row=0, column=0, sticky=tk.W)

        # Create data grid
        data_frame = ttkb.Frame(parent, padding=10)
        data_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create operation buttons
        button_frame = ttkb.Frame(parent, padding=10)
        button_frame.grid(row=2, column=0, sticky=tk.W)

        # Fetch table columns
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [col[0] for col in cursor.fetchall()]
            
            # Create entry fields
            self.create_entry_fields(columns, schema_frame)

            # Create data grid
            self.create_data_grid(table_name, columns, data_frame)

            # Create operation buttons
            self.create_operation_buttons(table_name, button_frame)

            cursor.close()
        except Error as e:
            logging.error(f"Error creating UI for {table_name}: {e}")

    def create_entry_fields(self, columns, parent):
        """Create entry fields for table columns"""
        for i, col in enumerate(columns):
            label = ttkb.Label(parent, text=col + ":")
            label.grid(row=i, column=0, sticky=tk.E, padx=5, pady=5)
            
            entry = ttkb.Entry(parent)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, f"{col}_entry", entry)

    def create_data_grid(self, table_name, columns, parent):
        """Create data grid using Treeview"""
        self.tree = ttkb.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttkb.Scrollbar(parent, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_table_data(table_name, columns)

    def load_table_data(self, table_name, columns):
        """Load data into Treeview"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            for row in data:
                self.tree.insert("", tk.END, values=row)
            cursor.close()
        except Error as e:
            logging.error(f"Error loading data for {table_name}: {e}")

    def create_operation_buttons(self, table_name, parent):
        """Create CRUD operation buttons"""
        insert_btn = ttkb.Button(parent, text="Insert", 
                              command=lambda: self.insert_data(table_name))
        insert_btn.grid(row=0, column=0, padx=5, pady=5)

        update_btn = ttkb.Button(parent, text="Update",
                              command=lambda: self.update_data(table_name))
        update_btn.grid(row=0, column=1, padx=5, pady=5)

        delete_btn = ttkb.Button(parent, text="Delete",
                              command=lambda: self.delete_data(table_name))
        delete_btn.grid(row=0, column=2, padx=5, pady=5)

        refresh_btn = ttkb.Button(parent, text="Refresh",
                               command=lambda: self.refresh_data(table_name))
        refresh_btn.grid(row=0, column=3, padx=5, pady=5)

    def insert_data(self, table_name):
        """Insert data into table"""
        try:
            cursor = self.connection.cursor()
            columns = [col for col in dir(self) if col.endswith('_entry')]
            values = [getattr(self, col).get() for col in columns]
            
            query = f"INSERT INTO {table_name} VALUES ({','.join(['%s']*len(values))})"
            cursor.execute(query, tuple(values))
            self.connection.commit()
            logging.info(f"Inserted data into {table_name}")
            self.refresh_data(table_name)
            cursor.close()
        except Error as e:
            logging.error(f"Insert error: {e}")

    def update_data(self, table_name):
        """Update selected data"""
        try:
            selected_item = self.tree.selection()[0]
            data = self.tree.item(selected_item, "values")
            cursor = self.connection.cursor()
            
            query = f"UPDATE {table_name} SET "
            query += ", ".join([f"{col}=%s" for col in data[1:]])
            query += f" WHERE {data[0]}=%s"
            
            cursor.execute(query, tuple(data[1:]))
            self.connection.commit()
            logging.info(f"Updated data in {table_name}")
            self.refresh_data(table_name)
            cursor.close()
        except Error as e:
            logging.error(f"Update error: {e}")

    def delete_data(self, table_name):
        """Delete selected data"""
        try:
            selected_item = self.tree.selection()[0]
            data = self.tree.item(selected_item, "values")
            cursor = self.connection.cursor()
            
            query = f"DELETE FROM {table_name} WHERE {data[0]}=%s"
            cursor.execute(query, (data[0],))
            self.connection.commit()
            logging.info(f"Deleted data from {table_name}")
            self.tree.delete(selected_item)
            cursor.close()
        except Error as e:
            logging.error(f"Delete error: {e}")

    def refresh_data(self, table_name):
        """Refresh data grid"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.load_table_data(table_name)

if __name__ == "__main__":
    root = ttkb.Window(themename="superhero")
    app = MySQLAdvancedGUI(root)
    root.mainloop()