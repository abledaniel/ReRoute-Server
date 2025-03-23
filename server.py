import requests
from supabase import create_client
import gtfs_realtime_pb2
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import pytz
import os

load_dotenv()

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)
pacific_tz = pytz.timezone("America/Los_Angeles")

def fetch_and_parse_gtfs():
    response = requests.get('https://api.octa.net/GTFSRealTime/protoBuf/VehiclePositions.aspx')
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    
    vehicle_data = []

    for entity in feed.entity:
        if entity.HasField('vehicle'):
            vehicle_info = entity.vehicle
            trip_info = vehicle_info.trip
            utc_dt = datetime.fromtimestamp(vehicle_info.timestamp).replace(tzinfo=pytz.utc)
            pacific_dt = utc_dt.astimezone(pacific_tz)
            # Prepare the data for uploading to Supabase
            vehicle_data.append({
                "trip_id": trip_info.trip_id,
                "start_date": trip_info.start_date,
                "schedule_relationship": trip_info.schedule_relationship,
                "route_id": trip_info.route_id,
                "latitude": vehicle_info.position.latitude,
                "longitude": vehicle_info.position.longitude,
                "bearing": vehicle_info.position.bearing,
                "odometer": vehicle_info.position.odometer,
                "speed": vehicle_info.position.speed,
                "current_stop_sequence": vehicle_info.current_stop_sequence,
                "current_status": vehicle_info.current_status,
                "congestion_level": vehicle_info.congestion_level,
                "vehicle_id": vehicle_info.vehicle.id,
                "vehicle_label": vehicle_info.vehicle.label,
                
                "timestamp": pacific_dt.isoformat()            })
    
    return vehicle_data

def store_in_supabase(data):
    try:
        response = supabase.table("trip_data").insert(data).execute()
        print(f"Data inserted successfully, {len(data)} records added")
        return response
    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        return None
    
def fetch_parse_and_upload():
    data = fetch_and_parse_gtfs()

    if data:
        store_in_supabase(data)

@app.get("/")
def read_root():
    return {"message": "The server is running"}

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_parse_and_upload, 'interval', minutes=1)
    scheduler.start()
    print("Scheduler started")
    uvicorn.run(app, host="0.0.0.0", port=8000)