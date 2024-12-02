import sys
import mysql.connector
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
from datetime import datetime
#Please note - Comments are ABOVE the line of code that is being commented

#Set the values for HOST, PASSWORD, and DATABASE variables so they are global
HOST = "localhost"
PASSWORD = "password"
DATABASE = "CS350 Project 1"

#Define method for login activities for users who sign in and out of the app
def log_activity(username, action):
    #Identify the .txt file we want to create/add to
    log_file = "user_activity_log.txt"
    #Set timestamp variable with current time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #Add the enteries to my user_activity_log.txt
    with open(log_file, "a") as file:
        file.write(f"Timestamp: {timestamp} | User: {username} | Action: {action}\n")

#Create WelcomeScreen class, open welcomescreen.ui
class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        #Set a fixed size for the window
        self.setFixedSize(500,350)
        #Hide password when logging in
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        #Take user to table selection once logged in
        self.selection.clicked.connect(self.loginfunction)
        #Disable window resizing
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

    #Attempting to log in as a user from the database
    def loginfunction(self):
        global user
        global password
        user = self.usernamefield.text()
        password = self.passwordfield.text()

        #If username/password field are empty, display an error message saying that
        if len(user) == 0 or len(password) == 0:
            self.error_label.setAlignment(Qt.AlignCenter) 
            self.error_label.setText("Enter username and password")

        else:
            try:
                connection = mysql.connector.connect(        
                    host=HOST,
                    user='root',  #MySQL user (you may need to change this)
                    password=PASSWORD,
                    database=DATABASE
                )
            
                #Create a cursor object to interact with the database
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM LogIn_Credential WHERE usernames = %s AND password = %s", (user, password))

                #Fetch the result of the query
                login_info = cursor.fetchall()

                if login_info:
                    #Extract the user's role from the query result
                    self.role = login_info[0][2]
                    #Successful login
                    print("Successfully logged in!")
                    #Close the cursor and database connection
                    cursor.close()
                    connection.close()
                    #Call the gotoselection method to transition to the next screen
                    self.gotoselection()
                    #Log the successful login
                    log_activity(user, "Logged in")
                
                #If user or pass are incorrect, throw an error
                else:
                    self.error_label.setAlignment(Qt.AlignCenter) 
                    self.error_label.setText("Invalid username or password")
                    #Close the cursor and the database connection
                    cursor.close()
                    connection.close()

            except mysql.connector.Error as err:
                #Handle MySQL errors if DB does not connect
                self.error_label.setAlignment(Qt.AlignCenter) 
                self.error_label.setText(f"MySQL Error: {err.msg}")

                #Close the cursor and connection in case of an error
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()

    #Bring the user to the table selection screen once logged in
    def gotoselection(self):
        #Record the inputs as variables for username and password
        user = self.usernamefield.text()
        password = self.passwordfield.text()
        #Passing my user, role, and password variables to the SelectTableScreen class
        self.select_table_screen = SelectTableScreen(user, self.role, password)
        #Establish a connection between signals and slots
        self.select_table_screen.table_selected.connect(self.show_selected_table)
        #Add a new widget to the stack of widgets managed by QStackedWidget
        widget.addWidget(self.select_table_screen)
        #Navigate to the next screen or widget in the stack
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    #Function for displaying the selected table (similar syntax to gotoselection())
    def show_selected_table(self, table_name):
        connection = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            database=DATABASE
        )
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]

        cursor.close()
        connection.close()

        #Initialize the ViewTable instance with the role information
        self.view_table_screen = ViewTable(column_names, self.role)
        self.view_table_screen.show_selected_table(table_name)
        widget.addWidget(self.view_table_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    #Record when the user logs out and add that to the user_activity_log.txt file
    def closeEvent(self, event):
        log_activity(user, "Logged out")
        event.accept()

    #Hide the error_label and success_label after a delay (e.g., 3 seconds)
    def hide_labels(self):
        self.error_label.hide()
        self.success_label.hide()

#Create TableScreen class, open tableviewer.ui
class SelectTableScreen(QDialog):
    #Define a signal to pass the selected table name
    table_selected = pyqtSignal(str)

    #Pass the variables and open selection.ui + set a fixed window size again
    def __init__(self, user, role, password):
        super(SelectTableScreen, self).__init__()
        self.user = user
        self.role = role
        self.password = password
        loadUi("selection.ui", self)
        self.setFixedSize(500,350)
        self.populate_table_selection()
        #Disable window resizing
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
    
    #Method to populate the table list with options available to the user
    def populate_table_selection(self):
        #Connect to the database using the user's role
        connection_role = mysql.connector.connect(
                host=HOST,
                user=self.role, 
                password='',
                database=DATABASE
        )
        cursor_role = connection_role.cursor()

        #Display table names granted to the role in question
        cursor_role.execute("SHOW TABLES")
        table_names = cursor_role.fetchall()

        cursor_role.close()
        connection_role.close()

        if table_names:
            #Populate the selection widget with table names
            for table_name in table_names:
                self.table_selection.addItem(table_name[0])
        else:
            self.table_selection.addItem("No tables available")

        #Connect the table_selection widget itemClicked signal to emit the selected table name
        self.table_selection.itemClicked.connect(self.on_table_selected)

    #Method responsible for handling the event when an item in the table selection widget is clicked
    def on_table_selected(self, item):
        #Get the selected table name
        selected_table = item.text()
        #Emit the selected table name
        self.table_selected.emit(selected_table)  
    
    #Record when the user logs out and add that to the user_activity_log.txt file
    def closeEvent(self, event):
            log_activity(user, "Logged out")
            event.accept()

    #Hide the error_label and success_label after a delay (e.g., 3 seconds)
    def hide_labels(self):
        self.error_label.hide()
        self.success_label.hide()

#Create UpdateWindow class, open update.ui
class UpdateWindow(QDialog):
    def __init__(self, table_name, id_value, *args):
        super(UpdateWindow, self).__init__()
        loadUi("update.ui", self)
        self.table_name = table_name
        #Ensure that id_value is not included in text_edits
        self.text_edits = [widget for widget in args if isinstance(widget, QTextEdit)]
        #When pushButton widget is clicked execute the query
        self.pushButton.clicked.connect(self.execute_update_query)
        #Save the id_value separately
        self.id_value = id_value
        #Disable window resizing
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

    #Define a method for executing an update query in a database
    def execute_update_query(self):
        try:
            #Establish a connection to the MySQL database using provided credentials
            connection = mysql.connector.connect(
                host=HOST,
                user='root',
                password=PASSWORD,
                database=DATABASE
            )
            
            #Create a cursor to interact with the database
            cursor = connection.cursor()

            #Fetch column names from the database table excluding the 'ID' column
            cursor.execute(f"SHOW COLUMNS FROM {self.table_name}")
            columns = [col[0] for col in cursor.fetchall() if col[0] != 'ID']

            #Initialize an empty list to store updates
            updates = []

            #Iterate through columns and corresponding text edits
            for column, edit in zip(columns, self.text_edits):
                #Get the text content from the text edit, strip whitespace
                value = edit.toPlainText().strip()
                #Check if there's a value in the text edit
                if value:
                    #Append the column name and its value to the updates list
                    updates.append(f"{column} = '{value}'")

            #Prepare the SET clause for the UPDATE query
            set_clause = ', '.join(updates)    
            #Get the ID value from a QTextEdit in the UI
            id_value = self.textEdit.toPlainText()            
            #Construct the UPDATE query using table name, set_clause, and ID value
            update_query = f"UPDATE {self.table_name} SET {set_clause} WHERE ID = {id_value}"
            #Execute the UPDATE query
            cursor.execute(update_query)
            log_activity(user, f"Query executed: {update_query}")
            #Commit the changes to the database
            connection.commit()
            #Close the cursor and the database connection
            cursor.close()
            connection.close()

            #Print success message and close the window
            self.success_label.setAlignment(Qt.AlignCenter)
            self.success_label.setText("Update query executed successfully!")
            self.close()

        except mysql.connector.Error as err:
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setText(f"Error executing UPDATE query: {err}")

    #Hide the error_label and success_label after a delay (e.g., 3 seconds)
    def hide_labels(self):
        self.error_label.hide()
        self.success_label.hide()

#Create ViewTable class, open tableviewer.ui
class ViewTable(QDialog):
    def __init__(self, column_names, role):
        #Initialize the ViewTable class
        super(ViewTable, self).__init__()
        #Set the role attribute for this instance
        self.role = role
        #Load the UI layout from the specified file ("tableviewer.ui")
        loadUi("tableviewer.ui", self)
        #Set a fixed size for the dialog window
        self.setFixedSize(770, 735)
        #Store column names received as input for later use
        self.column_names = column_names
        #Create a Qt standard item model to work with tabular data
        self.model = QStandardItemModel()
        #Set the model to the tableView widget for display
        self.tableView.setModel(self.model)
        #Set edit triggers to prevent editing within the tableView
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)
        #Create a QTimer instance to periodically refresh table data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_table_data)
        #Refresh interval set to 1 second
        self.timer.start(1000)
        #Initialize checkboxes with default labels
        self.init_checkboxes()
        #Call the method to lock column widths based on content
        self.lock_column_width()
        #Connect buttons to their respective query execution methods
        self.selectButton.clicked.connect(self.execute_select_query)
        self.insertButton.clicked.connect(self.execute_insert_query)
        self.updateButton.clicked.connect(self.execute_update_query)
        self.deleteButton.clicked.connect(self.execute_delete_query)
        #Disable window resizing
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

    #Method to lock the column width once it is set, to avoid table refreshes
    def lock_column_width(self):
        #Delay the execution to ensure the table is fully loaded
        QTimer.singleShot(100, self.set_column_widths)

    #Method to set column widths to 150 by default
    def set_column_widths(self):
        #Set the width of each column
        for i in range(len(self.column_names)):
            #150 represents the desired width
            self.tableView.setColumnWidth(i, 150)

    #Method to initialize checkbox widgets next to Select query option
    def init_checkboxes(self):
        #List of checkboxes present in the UI
        checkboxes = [self.checkBox, self.checkBox_2, self.checkBox_3, self.checkBox_4, self.checkBox_5]
        #Loop through each checkbox in the list
        for checkbox in checkboxes:
            #Set the text of each checkbox to an empty string
            #This effectively initializes or clears any existing text in the checkboxes
            checkbox.setText("")

    #Method to refresh table data
    def refresh_table_data(self):
        #Get the table name from the label text, assuming it starts with "Displaying "
        table_name = self.label.text().replace("Displaying ", "")
        #Get the selected columns to display
        selected_columns = self.get_selected_columns()
        #Check if there's a valid table name
        if table_name:
            try:
                connection = mysql.connector.connect(
                    host=HOST,
                    user='root',
                    password=PASSWORD,
                    database=DATABASE
                )
                cursor = connection.cursor()

                #Construct and execute the appropriate SELECT query based on selected columns
                if not selected_columns:
                    cursor.execute(f"SELECT * FROM {table_name}")
                else:
                    columns = ", ".join(selected_columns)
                    cursor.execute(f"SELECT {columns} FROM {table_name}")

                #Fetch the data and column names from the executed query
                data = cursor.fetchall()
                column_names = [i[0] for i in cursor.description]

                #Check if the number of columns in the table model matches the fetched data
                if self.model.columnCount() != len(column_names):
                    #If not matching, clear the existing model and set new column structure
                    self.model.clear()
                    self.model.setColumnCount(len(column_names))
                    self.model.setHorizontalHeaderLabels(column_names)
                    self.set_column_widths()

                #Clear existing rows to refresh the data
                self.model.removeRows(0, self.model.rowCount())

                #Insert fetched data into the table model
                for row_num, row_data in enumerate(data):
                    row_items = [QStandardItem(str(cell)) for cell in row_data]
                    self.model.insertRow(row_num, row_items)

                cursor.close()
                connection.close()

            except mysql.connector.Error as err:
                #Print error message if there's an issue with refreshing the data
                self.error_label.setText(f"Error refreshing table data: {err}")

    #Method to execute Select queries based on columns selected
    def execute_select_query(self):
        #Extract the table name from the label text, assuming it starts with "Displaying "
        table_name = self.label.text().replace("Displaying ", "")
        #Get the column names for the specified table
        column_names = self.get_column_names(table_name)
        #Populate checkboxes with retrieved column names
        self.populate_checkboxes(column_names)
        #Get the currently selected columns from the checkboxes
        selected_columns = self.get_selected_columns()
        #Check if any columns are selected
        if selected_columns:
            #Construct a comma-separated string of selected columns
            columns = ", ".join(selected_columns)
            
            #Check if a valid table name exists
            if table_name:
                try:
                    connection = mysql.connector.connect(
                        host=HOST,
                        user='root',
                        password=PASSWORD,
                        database=DATABASE
                    )
                    cursor = connection.cursor()
                    
                    #Construct and execute the SELECT query based on selected columns and table name
                    query = f"SELECT {columns} FROM {table_name}"
                    cursor.execute(query)
                    #Fetch the data and column names from the executed query
                    data = cursor.fetchall()
                    column_names = [i[0] for i in cursor.description]
                    #Clear the existing model and set new column structure
                    self.model.clear()
                    self.model.setColumnCount(len(column_names))
                    self.model.setHorizontalHeaderLabels(column_names)
                    #Insert fetched data into the table model
                    for row_num, row_data in enumerate(data):
                        row_items = [QStandardItem(str(cell)) for cell in row_data]
                        self.model.insertRow(row_num, row_items)

                    log_activity(user, f"Query executed: {query}")
                    cursor.close()
                    connection.close()

                except mysql.connector.Error as err:
                    self.error_label.setAlignment(Qt.AlignCenter)
                    #Set an error message if there's an issue executing the query
                    self.error_label.setText(f"Error executing SELECT query: {err}")
        else:
            self.error_label.setAlignment(Qt.AlignCenter)
            #Set an error message if no columns are selected
            self.error_label.setText("No columns selected")

    #Method to fetch and return column names
    def get_column_names(self, table_name):
        #Initialize an empty list to store column names
        column_names = []
        try:
            connection = mysql.connector.connect(
                host=HOST,
                user='root',
                password=PASSWORD,
                database=DATABASE
            )
            cursor = connection.cursor()
            #Fetch column information for the specified table
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            #Extract column names from the fetched data
            column_names = [col[0] for col in columns]
            cursor.close()
            connection.close()

        except mysql.connector.Error as err:
            #Set an error message if there's an issue fetching column names
            self.error_label.setText(f"Error fetching column names: {err}")

        return column_names

    #Method to label the select checkboxes with the column names
    def populate_checkboxes(self, column_names):
        #List of checkboxes present in the UI (assuming named as checkBox, checkBox_2, checkBox_3, etc.)
        checkboxes = [self.checkBox, self.checkBox_2, self.checkBox_3, self.checkBox_4, self.checkBox_5]

        #Loop through the checkboxes and corresponding column names
        for i, checkbox in enumerate(checkboxes):
            #Check if there are more checkboxes than column names
            if i < len(column_names):
                #Set the text of the checkbox to the corresponding column name
                checkbox.setText(column_names[i])
                #Make the checkbox visible
                checkbox.setVisible(True)
            else:
                #If no corresponding column name for the checkbox, hide the checkbox
                checkbox.setVisible(False)

    #Method to retrieve user's selection for select query
    def get_selected_columns(self):
        #List of checkboxes present in the UI (assuming named as checkBox, checkBox_2, checkBox_3, etc.)
        checkboxes = [self.checkBox, self.checkBox_2, self.checkBox_3, self.checkBox_4, self.checkBox_5]
        #List comprehension to retrieve text from checked checkboxes as selected columns
        selected_columns = [checkbox.text() for checkbox in checkboxes if checkbox.isChecked()]
        #Return the list of selected column names
        return selected_columns

    #Method to execute the insert query when Insert button is clicked
    def execute_insert_query(self):
        #Extract the table name from the label text, assuming it starts with "Displaying "
        table_name = self.label.text().replace("Displaying ", "")
        
        #Check access permissions based on table name and user role
        if (table_name == "Emp_SE" and self.role in ["HR", "PR", "General"]) or \
        (table_name == "Emp_HR" and self.role in ["PR", "General"]) or \
        (table_name == "Emp_PR" and self.role == "General"):
            #Set error message for denied access
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setText(f"Access denied: Read-only access for {table_name}")
            return
        
        #Proceed if table_name exists
        if table_name:
            #Get values from text edit fields
            values = [
                self.textEdit_5.toPlainText(),
                self.textEdit_6.toPlainText(),
                self.textEdit_7.toPlainText(),
                self.textEdit_8.toPlainText(),
                self.textEdit_9.toPlainText()
            ]
            try:
                #Establish connection to the database
                connection = mysql.connector.connect(
                    host=HOST,
                    user='root',
                    password=PASSWORD,
                    database=DATABASE
                )
                cursor = connection.cursor()
                
                #Fetch column names from the database for the specific table
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                column_names = [col[0] for col in cursor.fetchall()]

                #Construct the INSERT query dynamically based on the retrieved column names
                insert_query = f"INSERT INTO {table_name} ({', '.join([f'`{col}`' for col in column_names])}) VALUES ({','.join(['%s']*len(column_names))})"
                
                #Execute the dynamic INSERT query with the values
                cursor.execute(insert_query, values[:len(column_names)])  # Adjust values to match the number of columns
                
                #Commit the changes to the database
                connection.commit()
                log_activity(user, f"Query executed: {insert_query}")
                cursor.close()
                connection.close()
                
                #Set success message
                self.success_label.setAlignment(Qt.AlignCenter)
                self.success_label.setText("Insert query executed successfully!")
            except mysql.connector.Error as err:
                print(f"Error executing INSERT query: {err}")
                #Set error message for failed INSERT query
                self.error_label.setAlignment(Qt.AlignCenter)
                self.error_label.setText(f"Error executing INSERT query: {err}")

    #Method to deny access to those not permitted to update and and set the edit values to variables
    def execute_update_query(self):
        #Extract the table name from the label text, assuming it starts with "Displaying "
        table_name = self.label.text().replace("Displaying ", "")
        #Check access permissions based on table name and user role
        if table_name == "Emp_SE" and self.role in ["HR", "PR", "General"]:
            #Set error message for denied access and return
            #Align error message to center
            self.error_label.setAlignment(Qt.AlignCenter)  
            self.error_label.setText("Access denied: Read-only access for Emp_SE")
            return
        elif table_name == "Emp_HR" and self.role in ["PR", "General"]:
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setText("Access denied: Read-only access for Emp_HR")
            return
        elif table_name == "Emp_PR" and self.role == "General":
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setText("Access denied: Read-only access for Emp_PR")
            return
        
        #Get the ID value for the update operation
        id_value = self.get_selected_id()
        #Proceed if table_name and id_value exist
        if table_name and id_value:
            #Get the text edits where the user entered the new values
            value_edits = [
                self.textEdit_1, self.textEdit_2, self.textEdit_3,
                self.textEdit_4, self.textEdit_5
            ]

            #Open the update window with the table name, ID, and text edits for values
            self.open_update_window(table_name, id_value, *value_edits)
        else:
            #Set an error message if table name or ID for update is empty
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setText("Table name or ID to update is empty")

    #Method to open update window when Update button is pressed
    def open_update_window(self, table_name, id_value, *args):
        update_window = UpdateWindow(table_name, id_value, *args)
        #Pass references to labels from tableviewer.ui to update.ui
        #Pass the success_label reference
        update_window.success_label = self.success_label
        #Pass the error_label reference
        update_window.error_label = self.error_label
        #Show the update window
        update_window.show()
        update_window.exec_()

    #Method to get all values from ViewTable class to give to UpdateWindow
    def get_selected_id(self):
        #Initialize selected_id as None
        selected_id = None
        #List of label widgets where an ID might be stored
        label_widgets = [self.label_2, self.label_3, self.label_4, self.label_5, self.label_6]
        #Iterate through label widgets to find a non-empty label (assuming it holds the ID)
        for label in label_widgets:
            #Check if the label has text (assuming it holds the ID)
            if label.text():
                #Set the selected_id to the text of the label (the assumed ID)
                selected_id = label.text()
                #Break the loop if an ID is found in any label
                break
        #Return the selected_id (either the found ID or None if not found)
        return selected_id

    #Method to execute delete query when Delete button is pressed
    def execute_delete_query(self):
        #Extract the table name from the label text, assuming it starts with "Displaying "
        table_name = self.label.text().replace("Displaying ", "")
        
        #Check access permissions based on table name and user role
        if table_name == "Emp_SE" and self.role in ["HR", "PR", "General"]:
            #Set error message for denied access and return
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setText("Access denied: Read-only access for Emp_SE")
            return
        elif table_name == "Emp_HR" and self.role in ["PR", "General"]:
            self.error_label.setAlignment(Qt.AlignCenter) 
            self.error_label.setText("Access denied: Read-only access for Emp_HR")
            return
        elif table_name == "Emp_PR" and self.role == "General":
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setText("Access denied: Read-only access for Emp_PR")
            return

        #Get the ID to be deleted from the specified table
        id_to_delete = self.textEdit_12.toPlainText()
        #Proceed if both table_name and id_to_delete exist
        if table_name and id_to_delete:
            try:
                #Establish a connection to the MySQL database using provided credentials
                connection = mysql.connector.connect(
                    host=HOST,
                    user='root',
                    password=PASSWORD,
                    database=DATABASE
                )
                cursor = connection.cursor()

                #Construct and execute the DELETE query
                delete_query = f"DELETE FROM {table_name} WHERE ID = %s"
                cursor.execute(delete_query, (id_to_delete,))
                #Commit the changes to the database
                connection.commit()
                log_activity(user, f"Query executed: {delete_query}")
                cursor.close()
                connection.close()
                self.success_label.setAlignment(Qt.AlignCenter)
                self.success_label.setText("Delete query executed successfully!")
                #Refresh table data after deletion
                self.refresh_table_data()

            except mysql.connector.Error as err:
                #Set error message for failed DELETE query
                self.error_label.setAlignment(Qt.AlignCenter)
                self.error_label.setText(f"Error executing DELETE query: {err}")
        else:
            #Set an error message if table name or ID for deletion is empty
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setText("Table name or ID to delete is empty")

    #Method to show table to user
    def show_selected_table(self, table_name):
        #Fetch column names based on the selected table
        column_names = self.get_column_names(table_name)
        #Update checkboxes with actual column names
        self.populate_checkboxes(column_names)
        #Center align the title text
        self.label.setAlignment(Qt.AlignCenter)
        #Set label text to show the selected table name
        self.label.setText(f"Displaying {table_name}")
        connection = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            database=DATABASE
        )
        cursor = connection.cursor()
        #Execute the SQL query
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        #Get column names from the query result
        column_names = [i[0] for i in cursor.description]
        #Clear the existing data in the model
        self.model.clear()
        #Set the number of columns in the model
        self.model.setColumnCount(len(column_names))
        #Set column headers in the model
        self.model.setHorizontalHeaderLabels(column_names)

        #Iterate through fetched data
        for row_num, row_data in enumerate(data):
            #Create items for each cell in a row
            row_items = [QStandardItem(str(cell)) for cell in row_data]
            #Insert the row into the model
            self.model.insertRow(row_num, row_items)

        #Populating labels with column names if available
        label_widgets = [self.label_2, self.label_3, self.label_4, self.label_5, self.label_6]
        for i, col_name in enumerate(column_names[:5]):
            label_widgets[i].setText(col_name)

        #Close cursor and database connection
        cursor.close()
        connection.close()

    #Record when the user logs out and add that to the user_activity_log.txt file
    def closeEvent(self, event):
            log_activity(user, "Logged out")
            event.accept()

    #Hide the error_label and success_label after a delay (e.g., 3 seconds)
    def hide_labels(self):
        self.error_label.hide()
        self.success_label.hide()

#Main
app = QApplication(sys.argv)
widget = QStackedWidget()
welcome = WelcomeScreen()
widget.addWidget(welcome)
#Connect the aboutToQuit signal to log the user out when the application is about to close
app.aboutToQuit.connect(lambda: log_activity(user, "Logged out"))
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")
