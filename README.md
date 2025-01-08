Made By: Gurditt Singh Dadiala, Roll No. 22f3000636

Project Overview: The project is a library management system developed using Flask (building application), SQLite (data storage), Jinja2 templates (dynamically generate html templates), and Bootstrap (styling).

Programming languages needed: Python (Core Requirement - runs app.py), HTML, CSS

Project Setup: 
    1. Install Python: Ensure Python is installed on your system. You can download and install Python from the official website (https://www.python.org/).

    2. Create a Virtual Environment: Create a virtual environment for the project to isolate dependencies. Use the venv module to create the virtual environment.
    - Just change path to the project directory (cd path\to\your\project\directory)
    - now create the virtual environment (python -m venv venv)

    3. Activate Virtual Environment: Activate the virtual environment using the appropriate command for your operating system (source venv/bin/activate on Unix-based systems or venv\Scripts\activate on Windows).

    4. Install Dependencies: Download all the dependencies to run the project from the requirements.txt file using the python package installer (pip).
    - run (pip install requirements.txt)

    5. Run the Program: Finally, run the app.py file and a server will be hosted. Simply open your browser and follow the link (Ex: http://127.0.0.1:5000/) where the server is active and use the project.

Functionalities: Login via the provided passwords or use an online sqlite3 file to view the database content.
    ADMIN: {[username: a1, password: a1], [username: a2, password: a2]}
    USER: {[username: u1, password: u1]}

    Some functionalities include:
    - User Registration/Login
    - User/Admin Dashboard
    - Add/Edit/Delete Sections/Books (Section/Book management - Admins Only)
    - Assign a different section to a Book (Admins Only)
    - Auto Revoke after 7 days
    - User can request upto 5 e-books
    - Grant/Revoke Book Access (Admins Only)
    - View feedback/ratings (Admins Only)
    - Issue(Request)/Return Books (Users Only)
    - Give feedback to books (Users Only)
    - Search Functionality based on Author, Section
