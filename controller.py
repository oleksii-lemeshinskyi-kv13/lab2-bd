from model import Model
from view import View


class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View()

    def run(self):
        while True:
            choice = self.show_menu()
            if choice == '1':
                self.table_names()
            elif choice == '2':
                self.table_columns()
            elif choice == '3':
                self.table_data()
            elif choice == '4':
                self.insert_data()
            elif choice == '5':
                self.update_data()
            elif choice == '6':
                self.delete_data()
            elif choice == '7':
                self.generate_data()
            elif choice == '8':
                self.custom_query_1()
            elif choice == '9':
                self.custom_query_2()
            elif choice == '10':
                self.custom_query_3()
            elif choice == '0':
                break
            else:
                self.view.show_message("Invalid choice!")

    def show_menu(self):
        self.view.show_message("\nMenu:")
        self.view.show_message("1. Table names")
        self.view.show_message("2. Table columns")
        self.view.show_message("3. Table data (first 10 rows)")
        self.view.show_message("4. Insert data")
        self.view.show_message("5. Update data")
        self.view.show_message("6. Delete data")
        self.view.show_message("7. Generate data")
        self.view.show_message("8. Custom query 1")
        self.view.show_message("9. Custom query 2")
        self.view.show_message("10. Custom query 3")
        self.view.show_message("0. Exit")
        return input("Enter your choice: ")

    def table_names(self):
        names = self.model.table_names()
        self.view.show_message("Table names:")
        self.view.show_table_names(names)
        
    def table_columns(self):
        table_name = self.view.get_table_name()
        columns = self.model.table_columns(table_name)
        self.view.show_message("Table columns:")
        self.view.show_table_columns(columns)
        
    def table_data(self):
        table_name = self.view.get_table_name()
        data = self.model.table_data(table_name)
        columns = self.model.table_columns(table_name)
        self.view.show_message("Table data:")
        self.view.show_table_data(columns, data)
        
    def insert_data(self):
        table_name = self.view.get_table_name()
        columns = self.model.table_columns(table_name)
        # delete id column
        columns = columns[1:]
        data = self.view.get_data(columns)
        if self.model.insert_data(table_name, columns, data):
            self.view.show_message("Data inserted successfully!")
        else:
            self.view.show_message("Data insertion failed!")
        
    def update_data(self):
        table_name = self.view.get_table_name()
        columns = self.model.table_columns(table_name)
        id_name = columns[0]
        id_value = self.view.get_data([id_name])[0]
        # delete id column
        columns = columns[1:]
        data = self.view.get_data(columns)
        if self.model.update_data(table_name, columns, data, id_name, id_value):
            self.view.show_message("Data updated successfully!")
        else:
            self.view.show_message("Data updation failed!")
        
    def delete_data(self):
        table_name = self.view.get_table_name()
        id_name = self.model.table_columns(table_name)[0]
        id_value = self.view.get_data([id_name])[0]
        if self.model.delete_data(table_name, id_name, id_value):
            self.view.show_message("Data deleted successfully!")
        else:
            self.view.show_message("Data deletion failed!")
        
    def generate_data(self):
        table_name = self.view.get_table_name()
        rows = int(self.view.get_input("Enter number of rows: "))
        if self.model.generate_data(table_name, rows):
            self.view.show_message("Data generated successfully!")
        else:
            self.view.show_message("Data generation failed!")
    
    def custom_query_1(self):
        mentor_name_pattern = self.view.get_input("Enter mentor name pattern: ")
        mentor_min_id = self.view.get_input("Enter mentor min id: ")
        mentor_max_id = self.view.get_input("Enter mentor max id: ")
        columns, result, t = self.model.custom_query_1(mentor_name_pattern, mentor_min_id, mentor_max_id)
        if result is not None:
            self.view.show_table_data(columns, result)
            self.view.show_message(f"Query executed successfully in {t} seconds!")
        else:
            self.view.show_message("Query execution failed!")
    
    def custom_query_2(self):
        project_title_pattern = self.view.get_input("Enter project title pattern: ")
        columns, result, t = self.model.custom_query_2(project_title_pattern)
        if result is not None:
            self.view.show_table_data(columns, result)
            self.view.show_message(f"Query executed successfully in {t} seconds!")
        else:
            self.view.show_message("Query execution failed!")
    
    def custom_query_3(self):
        columns, result, t = self.model.custom_query_3()
        if result is not None:
            self.view.show_table_data(columns, result)
            self.view.show_message(f"Query executed successfully in {t} seconds!")
        else:
            self.view.show_message("Query execution failed!")
    
        
