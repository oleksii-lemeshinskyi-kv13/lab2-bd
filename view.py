import tabulate

class View:
    def show_message(self, message):
        print(message)
        
    def show_table_names(self, names):
        print(names)
        
    def show_table_columns(self, columns):
        print(columns)
        
    def get_table_name(self):
        return input("Enter table name: ")
    
    def show_table_data(self, columns, data):
        print(tabulate.tabulate(tabular_data=data, 
                                headers=columns, 
                                tablefmt='grid'))
        
    def get_data(self, columns):
        data = []
        for column in columns:
            data.append(input(f"Enter '{column}' column: "))
        return tuple(data)
    
    def get_input(self, message):
        return input(message)
    
        
