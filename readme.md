To run project, follow these steps:
1. In backend/settings.py at line number 80 enter your postgres details and add your postgres password in .env file.

2. Open the terminal in Visual Studio Code (VSCode) and navigate to the "store-monitoring" directory:
   pip install django
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver

3. Navigate to these urls to insert data from csv files to database:
  http://127.0.0.1:8000/insert_store_status/
  http://127.0.0.1:8000/insert_menu_hours/
  http://127.0.0.1:8000/insert_time_zone/

4. Navigate to this url to trigger generation of report file and get the report_id:
  http://127.0.0.1:8000/trigger_report

5. Navigate to this url to get the report file:
  http://127.0.0.1:8000/get_report/report_id/ (report_id is provided at above url)
