# PythonDatabaseApp
My project is a code that is part of a PyQt5-based Python application designed to create a graphical user interface (GUI) for a database management system. The application facilitates user authentication, after which users can select and view database tables according to their respective roles. The primary goal of the project is to provide a user-friendly interface for interacting with a MySQL database.
The goal of the project is to create an application that allows users to log in to a database and select database tables to view based on their roles. This can be particularly useful in scenarios where different users have varying degrees of access to different parts of the database. The code aims to provide a mechanism for user authentication, followed by the ability to choose tables to interact with.
I developed this code on my own. I researched many different options for how this could be done, and Python was the most compatible on MacOS. I researched how to use PyQt 5 to configure my GUI on Youtube and Stack overflow. I am the sole creator/contributor of this code.
Description:
- Dataset (Tables, Attributes):
- The code interacts with a MySQL database. It references a table named
"LogIn_Credential" with at least three attributes: "usernames," "password," and a role- related attribute, which is used to determine the user's role. Additionally, other tables have columns that designate various attributes.

Operation Flow of the Project:
1. The user launches the application, which opens the WelcomeScreen.
2. The WelcomeScreen prompts the user for a username and password.
3. When the user clicks the Log In button, the code tries to authenticate the user by
checking their credentials against the "LogIn_Credential" table in the MySQL database.
4. If the credentials are valid, the code retrieves the user's role from the database and
opens the SelectTableScreen.
5. The SelectTableScreen displays a list of tables based on the user's role. The user can
select a table to work with.
6. Once a table is selected a window displaying that table opens
7. The user can select the x in the top left corner of the window to exit

Implementation:
  - The code uses PyQt5 for creating the GUI.
  - It establishes a connection to a MySQL database using the provided credentials (HOST,
  PASSWORD, DATABASE).
  - The WelcomeScreen class handles user authentication, including checking if the username and
  password fields are empty and verifying the credentials in the "LogIn_Credential" table.
  - The SelectTableScreen class populates a dropdown widget with table names from the database, based on the user's role.
  - The ViewTable class opens the table for the user to view with a Select statement from MySQL
  - The main part of the code initializes the application, sets up the GUI with the WelcomeScreen,
  and allows the user to navigate to the SelectTableScreen upon successful login.
  The code provided is the foundation for an application that aims to provide a GUI for interacting with a MySQL database. It focuses on user authentication and role-based access to database tables. However, it's worth noting that the code is a partial implementation and lacks details on how users can interact/update the selected database tables. Additional features such as editing and viewing data within the tables would need to be added to make it a fully functional database management tool.
