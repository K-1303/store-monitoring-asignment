To run the project, please follow the steps below:

Step 1: Set up the PostgreSQL Database

    Open the backend/settings.py file and go to line number 80.
    Enter your PostgreSQL database details, such as host, port, database name, username, and password.
    Create a .env file in the root directory of your project.
    Add your PostgreSQL password to the .env file.

Step 2: Install Dependencies and Run the Server

    Open the terminal in Visual Studio Code (VSCode) and navigate to the "store-monitoring" directory.
    Install Django by running the following command: pip install django.
    Apply the database migrations by running: python manage.py makemigrations followed by python manage.py migrate.
    Start the development server by running: python manage.py runserver.

Step 3: Insert Data from CSV Files to Database

    Open your web browser and visit the following URLs one by one:
        http://127.0.0.1:8000/insert_store_status/
        http://127.0.0.1:8000/insert_menu_hours/
        http://127.0.0.1:8000/insert_time_zone/
    Each URL corresponds to inserting data from a specific CSV file into the database.

Step 4: Generate a Report and Retrieve Report ID

    Visit the following URL to trigger the generation of a report file and retrieve the report ID:
        http://127.0.0.1:8000/trigger_report
    This URL will generate the report file and provide you with a unique report ID.

Step 5: Retrieve the Report File

    To retrieve the report file, use the following URL:
        http://127.0.0.1:8000/get_report/report_id/
    Replace report_id in the URL with the actual report ID obtained from Step 4.
    This URL will allow you to download the generated report file.
