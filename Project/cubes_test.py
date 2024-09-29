import paho.mqtt.client as mqtt 
import time
import random

# broker IP address:
broker = "broker.hivemq.com"
running_time = 180 # in sec
port = 8000  # for using web sockets
global ON
ON = True
client_TRH = 20

def on_log(client, userdata, level, buf):
    print("log: " + buf)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
        # Subscribe to the topic only after connection is successful
        client.subscribe("pr/home/semC/2024/cold_system/DHT/sts")
        print("Subscribed successfully!")
    else:
        print("Bad connection. Returned code =", rc)

def on_disconnect(client, userdata, rc=0):
    print("Disconnected. Result code:", str(rc))

def on_message(client, userdata, msg):
    global ON
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    print("Message received:", m_decode)
    ON = msg_parse_temp(m_decode)
    send_msg_to_relay(client)

def msg_parse_temp(m_decode):
    print(m_decode)
    try:
        # Split the string to find the temperature part
        temp_str = m_decode.split("Temperature: ")[1].split(" ")[0]
        # Convert the temperature to an integer by rounding it
        temp_value = round(float(temp_str))  # Convert to float first, then round and convert to int
        print(f"Parsed Temperature Value: {temp_value}")
        result = temp_value > client_TRH
        print(result)
        return result
    except (IndexError, ValueError) as e:
        print(f"Error parsing temperature: {e}")
        return False

# Global variable to track the relay state
relay_state = False

def send_msg_to_relay(client):
    global ON, relay_state
    
    if ON and not relay_state:
        device_ID = "RELAY/sts"  # RELAY TOPIC
        # Create a message to turn on the relay
        relay_message = '{"type":"set_state", "action":"set_value", "addr":0, "cname":"ONOFF", "value":1}'
        print("Turning on relay with message:", relay_message)
        client.publish(f"pr/home/semC/2024/cold_system/{device_ID}", relay_message)
        relay_state = True  # Update relay state to ON
    elif not ON and relay_state:
        device_ID = "RELAY/sts"  # RELAY TOPIC
        # Create a message to turn off the relay
        relay_message = '{"type":"set_state", "action":"set_value", "addr":0, "cname":"ONOFF", "value":0}'
        print("Turning off relay with message:", relay_message)
        client.publish(f"pr/home/semC/2024/cold_system/{device_ID}", relay_message)
        relay_state = False  # Update relay state to OFF
    else:
        print("Relay state unchanged. ON:", ON, "Relay State:", relay_state)


r = random.randrange(1, 10000)  # for creating unique client ID
clientname = "IOT_test-" + str(r)

# Create a new client instance using WebSocket
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, clientname, transport="websockets")
client.on_connect = on_connect  # Bind callback functions
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_log = on_log  # Enable logging for debugging

print("Connecting to broker", broker)
client.connect(broker, port)  # Connect to the broker

# Start the loop
client.loop_start()

# Keep the script running for the specified time
time.sleep(running_time)

# Stop the loop and disconnect
client.loop_stop()
client.disconnect()
print("End of script run")
