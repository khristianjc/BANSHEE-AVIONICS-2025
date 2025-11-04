from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import math

# -------------------- CONNECT TO VEHICLE --------------------
connection_string = 'tcp:127.0.0.1:5762'
print("Connecting to vehicle...")
vehicle = connect(connection_string, wait_ready=True)

# --- Connect to Pixhawk via USB cable ---
# connection_string = (example) 'COM14'
# vehicle = connect(connection_string, baud=57600, wait_ready=True)

# --- Connect to Pi ---
# connection_string = (example) '/dev/ttyAMA0'
# vehicle = connect(connection_string, baud=57600, wait_ready=True)

# -------------------- ARM AND TAKEOFF FUNCTION --------------------
def arm_and_takeoff(target_altitude):
    print("\nArming motors...")
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialize...")
        time.sleep(1)

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(target_altitude)

    # Wait until the vehicle reaches target altitude
    while True:
        alt = vehicle.location.global_relative_frame.alt
        print(f" Altitude: {alt:.2f} m")
        if alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# -------------------- CALCULATE RELATIVE GPS COORDINATE --------------------
def get_location_metres(original_location, dNorth, dEast, alt):
    """
    Returns a LocationGlobalRelative object moved dNorth and dEast metres from original_location.
    """
    earth_radius = 6378137.0  # radius of Earth in meters
    new_lat = original_location.lat + (dNorth / earth_radius) * (180 / math.pi)
    new_lon = original_location.lon + (dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))) * (180 / math.pi)
    return LocationGlobalRelative(new_lat, new_lon, alt)

# -------------------- MAIN SEQUENCE --------------------
target_altitude = 10

# Takeoff
arm_and_takeoff(target_altitude)

# Record home GPS location
home_location = vehicle.location.global_frame
print("\nHome location recorded:")
print(f" Latitude: {home_location.lat}")
print(f" Longitude: {home_location.lon}")
print(f" Altitude: {home_location.alt}")

# Move 10 m North from home, stay at 10 m altitude
target_location = get_location_metres(home_location, dNorth=10, dEast=0, alt=target_altitude)
print("\nFlying 10 meters north of takeoff point...")
vehicle.simple_goto(target_location)

# Hover for 10 seconds at new location
time.sleep(10)

# Return to home position
print("Returning to home location...")
return_location = get_location_metres(home_location, dNorth=0, dEast=0, alt=target_altitude)
vehicle.simple_goto(return_location)
time.sleep(10)

# Land
print("Landing...")
vehicle.mode = VehicleMode("LAND")

# Wait until landed
while vehicle.armed:
    print(" Waiting for landing...")
    time.sleep(1)

print("Landed and disarmed.")
vehicle.close()
