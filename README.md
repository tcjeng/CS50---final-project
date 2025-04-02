My Reads Web Application
#### Video Demo:  (https://youtu.be/QDCtD456CNc)
#### Description:
The "My Reads" web application is designed to help users track their reading progress by providing a platform where they can manage their books and set personal reading goals. The app is built using Flask, a lightweight web framework for Python, and utilizes an SQLite database to store user data, including books and reading goals. The app’s key features include user authentication, the ability to add and manage books, and a new feature that allows users to set and track their reading goals.

#### Purpose of the Application
The primary purpose of the My Reads application is to offer an organized and easy-to-use platform for book lovers to keep track of the books they’ve read, are currently reading, or plan to read. Additionally, the app provides an option to set a personal reading goal, enabling users to define how many books they wish to read and by when. The goal-setting feature helps users stay motivated by providing a clear target to achieve. This application is designed with simplicity and user experience in mind, ensuring that even new users can easily navigate through the interface and use its core features.

#### Key Features and Functionality
The My Reads application includes several key features to make the reading and goal-setting process more manageable:

- User Authentication: The app allows users to register and log in with their credentials. Once logged in, users are directed to their personalized reading list. If the user is not logged in, they are prompted to log in or register. This ensures that each user's data is kept private and secure.

- Reading List Management: Users can add books to their reading list, including details like the book title, author, genre, page count, and status (e.g., "Reading", "Completed", "To Read"). The app displays this information in a clean and easy-to-read table format on the homepage. Users can also edit or delete books from their list, making it easy to update or remove books as they progress.

- Setting a Reading Goal: The app’s new feature allows users to set a reading goal by defining how many books they want to read and by what date. This goal is stored in the database and can be viewed and updated on the homepage. If no goal is set, users are encouraged to set one, and a link to the goal-setting page is provided. This feature is designed to keep users motivated and focused on achieving their reading targets.

- Flash Messages: The app uses flash messages to provide users with feedback after actions like registering, logging in, setting a reading goal, or adding a book. These messages help inform users if they have successfully completed an action or if there was an error (e.g., missing fields in a form).

#### Application Flow and Code Explanation
The app follows a structured flow to ensure that users can interact with their reading list and goal seamlessly. Here's a breakdown of the key functions and routes:

- Registration and Login: The register and login routes handle the user authentication process. When a user registers, their username and password are securely stored in the database after hashing the password. Upon logging in, the user is redirected to the homepage (/), where their reading list and reading goal (if set) are displayed. If a user is not logged in, they are redirected to the login page.

- Setting a Reading Goal: The goal route is responsible for setting or updating a reading goal. When a user visits the "/goal" page, they can input the number of books they aim to read and a target date. This data is saved in the reading_goals table. If the user already has a goal, they can update it by entering new values. The goal is displayed on the homepage once set, and users can see how many books they have left to read before reaching their target.

- Displaying the Reading List: The index route fetches all books associated with the logged-in user from the database and displays them in a table format. Users can add, edit, or delete books from their reading list through the respective forms and buttons. If no books are added, the app encourages users to start adding books or set a reading goal.

- Goals and books edit and deletion: Users also have the option to delete or edit their reading goal and their reading lists. If the user wants to change a goal or a book, they can delete or edit it with a simple click of a button.

- Session Management: Throughout the app, session variables are used to keep track of the logged-in user. The session stores the user’s ID and username, ensuring that they are only able to access and modify their own data. If the user is not logged in, they are redirected to the login page.

- Database Interaction: The app uses an SQLite database to store user information, books, and reading goals. The database schema includes tables for users, books, and reading_goals. The app interacts with the database using SQL queries to insert, update, select, and delete data as needed.
