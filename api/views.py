import csv
from datetime import datetime, time
from django.http import JsonResponse
from .models import StoreActivity, StoreBusinessHours, StoreTimezone, Report
from django.http import JsonResponse, HttpResponse
import os
from django.utils import timezone 
from datetime import timedelta
from pytz import timezone

report_list = []

def insert_store_status(request):
    data = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data\store status.csv')
    with open(data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  

        for row in reader:
            store_id = int(float(row[0]))  
            try:
                timestamp_str = row[2].replace(' UTC', '')  
                timestamp_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                continue  
            status = row[1]

            store_activity = StoreActivity(
                store_id=store_id,
                timestamp_utc=timestamp_utc,
                status=status
            )
            store_activity.save()

    return JsonResponse({'status': 'success', 'message': 'Data imported successfully'})

def insert_menu_hours(request):
    data = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data\Menu hours.csv')
    with open(data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  

        for row in reader:
            store_id = int(row[0])
            day_of_week = int(row[1])
            start_time_str = row[2]
            end_time_str = row[3]

            start_time_local = time.fromisoformat(start_time_str)
            end_time_local = time.fromisoformat(end_time_str)

            store_business_hours = StoreBusinessHours(
                store_id=store_id,
                day_of_week=day_of_week,
                start_time_local=start_time_local,
                end_time_local=end_time_local
            )
            store_business_hours.save()

    return JsonResponse({'status': 'success', 'message': 'Data imported successfully'})

def insert_time_zone(request):
    data = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data\\bq-results-20230125-202210-1674678181880.csv')
    with open(data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  

        for row in reader:
            store_id = int(row[0])
            timezone_str = row[1] if row[1] else 'America/Chicago'

            store_timezone = StoreTimezone(
                store_id=store_id,
                timezone_str=timezone_str
            )
            store_timezone.save()

    return JsonResponse({'status': 'success', 'message': 'Data imported successfully'})

def calculate_uptime(activity_data, start_time_interval, end_time_interval, start_time_local, end_time_local):
    uptime = 0

    sorted_data = activity_data.order_by('timestamp_utc')

    for i in range(len(sorted_data) - 1):
        current_activity = sorted_data[i]
        next_activity = sorted_data[i + 1]

        # Calculate the duration between current and next activity
        duration = (next_activity.timestamp_utc - current_activity.timestamp_utc).total_seconds() / 60

        # Adjust start and end times based on business hours
        start_time = max(current_activity.timestamp_utc, start_time_interval)
        end_time = min(next_activity.timestamp_utc, end_time_interval)

        # Check if the activity falls within business hours
        if start_time.time() >= start_time_local and end_time.time() <= end_time_local:
            uptime += (end_time - start_time).total_seconds() / 60

    return uptime


from django.contrib.postgres.aggregates import ArrayAgg

def generate_report():
    current_time_utc = datetime.now(timezone('UTC'))

    report_data = {
        'store_id': [],
        'uptime_last_hour': [],
        'uptime_last_day': [],
        'uptime_last_week': [],
        'downtime_last_hour': [],
        'downtime_last_day': [],
        'downtime_last_week': [],
    }

    stores = StoreBusinessHours.objects.all()[:10]  # Limiting to 100 stores
    for store in stores:
        store_id = store.store_id
        timezone_obj = StoreTimezone.objects.filter(store_id=store_id).first()
        timezone_str = timezone_obj.timezone_str
        
        business_hours = StoreBusinessHours.objects.filter(store_id=store_id)
        if not business_hours.exists():
            # If business hours data is missing, assume the store is open 24*7
            start_time_local = datetime.min.time()
            end_time_local = datetime.max.time()
        else:
            # Get the start and end time of the store's business hours in local time
            business_hours = business_hours.first()
            start_time_local = business_hours.start_time_local
            end_time_local = business_hours.end_time_local

        # Convert the current time to the store's local timezone
        store_timezone = timezone(timezone_str)
        current_time_local = current_time_utc.astimezone(store_timezone)

        # Calculate the start and end time for the last hour, last day, and last week
        start_time_last_hour = current_time_local - timedelta(hours=1)
        start_time_last_day = current_time_local - timedelta(days=1)
        start_time_last_week = current_time_local - timedelta(weeks=1)

        # Get the store's activity data within the specified time intervals
        activity_last_hour = StoreActivity.objects.filter(
            store_id=store_id,
            timestamp_utc__gte=start_time_last_hour,
            timestamp_utc__lte=current_time_utc
        )
        activity_last_day = StoreActivity.objects.filter(
            store_id=store_id,
            timestamp_utc__gte=start_time_last_day,
            timestamp_utc__lte=current_time_utc
        )
        activity_last_week = StoreActivity.objects.filter(
            store_id=store_id,
            timestamp_utc__gte=start_time_last_week,
            timestamp_utc__lte=current_time_utc
        )

        # Calculate the uptime and downtime for each time interval
        uptime_last_hour = calculate_uptime(activity_last_hour, start_time_last_hour, current_time_local, start_time_local, end_time_local)
        uptime_last_day = calculate_uptime(activity_last_day, start_time_last_day, current_time_local, start_time_local, end_time_local)
        uptime_last_week = calculate_uptime(activity_last_week, start_time_last_week, current_time_local, start_time_local, end_time_local)

        downtime_last_hour = (current_time_local - start_time_last_hour).total_seconds() / 60 - uptime_last_hour
        downtime_last_day = (current_time_local - start_time_last_day).total_seconds() / 3600 - uptime_last_day
        downtime_last_week = (current_time_local - start_time_last_week).total_seconds() / 3600 - uptime_last_week

        # Update the report data
        report_data['store_id'].append(store_id)
        report_data['uptime_last_hour'].append(uptime_last_hour)
        report_data['uptime_last_day'].append(uptime_last_day)
        report_data['uptime_last_week'].append(uptime_last_week)
        report_data['downtime_last_hour'].append(downtime_last_hour)
        report_data['downtime_last_day'].append(downtime_last_day)
        report_data['downtime_last_week'].append(downtime_last_week)

    # Save the report data to the database
    report = Report.objects.create(**report_data)
    return [report]



def trigger_report(request):
    # Generate the reports
    reports = generate_report()

    # Generate the CSV data
    csv_data = generate_csv(reports)

    # Create the response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'
    writer = csv.writer(response)
    writer.writerow(['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week',
                     'downtime_last_hour', 'downtime_last_day', 'downtime_last_week'])
    writer.writerow(csv_data)  # Write the CSV data as a single row

    # Return a single report ID as a response
    return JsonResponse({"report_id": reports[0].id})


def generate_csv(report_list):
    csv_data = []

    for report in report_list:
        csv_data.append([
            str(report.store_id),
            str(report.uptime_last_hour),
            str(report.uptime_last_day),
            str(report.uptime_last_week),
            str(report.downtime_last_hour),
            str(report.downtime_last_day),
            str(report.downtime_last_week)
        ])

    return csv_data

def get_report(request, report_id):
    if not Report.objects.filter(id=report_id).exists():
        return JsonResponse({"message": "Report not found"})

    report = Report.objects.get(id=report_id)

    # Convert the single report into a list containing only one report
    reports = [report]

    csv_data = generate_csv(reports)

    # Extract the values from the csv_data
    values = csv_data[0]
    column_headers = ['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'downtime_last_hour', 'downtime_last_day', 'downtime_last_week']

    # Create key-value pairs from the values
    key_value_pairs = [(column, value) for column, value in zip(column_headers, values)]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'
    writer = csv.writer(response)
    writer.writerows(key_value_pairs)

    return response





    
    




