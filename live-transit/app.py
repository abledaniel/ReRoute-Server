from flask import Flask, jsonify, request
from flask_cors import CORS
import gtfs_realtime_pb2
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/vehicle-positions/<route_id>', methods=['GET'])
def get_vehicle_positions_by_route(route_id):
    try:
        response = requests.get('https://api.octa.net/GTFSRealTime/protoBuf/VehiclePositions.aspx')
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        vehicles = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                vehicle = entity.vehicle
                # Filter by route_id
                if vehicle.trip.route_id == route_id:
                    vehicles.append({
                        "trip_id": vehicle.trip.trip_id,
                        "route_id": vehicle.trip.route_id,
                        "latitude": vehicle.position.latitude,
                        "longitude": vehicle.position.longitude,
                        "timestamp": vehicle.timestamp,
                        "trip_id": vehicle.trip.trip_id
                    })
        
        return jsonify({
            'success': True,
            'count': len(vehicles),
            'vehicles': vehicles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)