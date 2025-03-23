import gtfs_realtime_pb2
import requests

response = requests.get('https://api.octa.net/GTFSRealTime/protoBuf/VehiclePositions.aspx')
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

for entity in feed.entity:
    # if entity.HasField('trip_update'):
    #     print(entity.trip_update)
    if entity.HasField('vehicle'):
        print(entity.vehicle)
    # elif entity.HasField('alert'):
    #     print(entity.alert)

