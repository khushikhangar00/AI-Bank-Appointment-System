import urllib.request
import json
import time

def test_api():
    print("Booking...")
    data = json.dumps({
        'customer_id': 'C999', 
        'name': 'Test', 
        'mobile': '1234567890', 
        'purpose': 'Other', 
        'preferred_date': '2027-01-01', 
        'preferred_time': '10:00-10:30'
    }).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:5000/api/book', data=data, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))
    print(result)
    
    app_id = result['appointment_id']
    print(f"Got appointment ID: {app_id}")
    
    print("Queue...")
    req2 = urllib.request.Request('http://127.0.0.1:5000/api/queue')
    response2 = urllib.request.urlopen(req2)
    q = json.loads(response2.read().decode('utf-8'))
    print(f"Queue length: {len(q)}")
    
    print("Confirming...")
    req3 = urllib.request.Request(f'http://127.0.0.1:5000/api/confirm/{app_id}', data=b'', method='POST')
    response3 = urllib.request.urlopen(req3)
    print(json.loads(response3.read().decode('utf-8')))

if __name__ == '__main__':
    time.sleep(2) # Give server time to start
    test_api()
