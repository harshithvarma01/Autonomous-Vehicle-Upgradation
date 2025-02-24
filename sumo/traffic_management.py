import os
import sys
import traci
import random

# Import SUMO libraries
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

def start_simulation():
    # Start SUMO with TraCI
    if sys.platform.startswith('win'):
        sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
    else:
        sumo_binary = 'sumo-gui'
    
    sumo_cmd = [
        sumo_binary,
        "-c", "map.sumocfg",
        "--remote-port", "8813",  # Specify a port
        "--start",
        "--quit-on-end",
        "--device.rerouting.probability", "1.0",
        "--device.rerouting.period", "30",
        "--error-log", "sumo-errors.log"  # Log errors
    ]
    
    try:
        traci.start(sumo_cmd)
        print("Successfully connected to SUMO")
    except Exception as e:
        print(f"Error starting SUMO: {e}")
        sys.exit(1)

def simulate_accident(edge_id, lane_index=0, position=50):
    """Simulate an accident by closing a lane and triggering rerouting"""
    try:
        lane_id = f"{edge_id}_{lane_index}"
        
        # Check if lane exists
        if lane_id not in traci.lane.getIDList():
            print(f"Warning: Lane {lane_id} not found")
            return
            
        # Close the lane where accident occurred
        traci.lane.setMaxSpeed(lane_id, 0)
        traci.lane.setDisallowed(lane_id, ["passenger"])
        
        # Get all active vehicles
        vehicles = traci.vehicle.getIDList()
        
        # Trigger rerouting for all vehicles
        for vehicle_id in vehicles:
            try:
                if traci.vehicle.getRouteID(vehicle_id) != "":
                    traci.vehicle.rerouteTraveltime(vehicle_id)
            except traci.TraCIException as e:
                print(f"Warning: Could not reroute vehicle {vehicle_id}: {e}")
                continue
                
        print(f"Successfully simulated accident on lane {lane_id}")
        
    except Exception as e:
        print(f"Error in simulate_accident: {e}")

def remove_accident(edge_id, lane_index=0):
    """Remove accident conditions and restore normal traffic flow"""
    try:
        lane_id = f"{edge_id}_{lane_index}"
        
        # Check if lane exists
        if lane_id not in traci.lane.getIDList():
            print(f"Warning: Lane {lane_id} not found")
            return
            
        traci.lane.setMaxSpeed(lane_id, -1)  # Restore default speed
        traci.lane.setAllowed(lane_id, ["passenger"])  # Restore default vehicle classes
        print(f"Successfully removed accident from lane {lane_id}")
        
    except Exception as e:
        print(f"Error in remove_accident: {e}")

def run_simulation():
    print("Starting simulation...")
    start_simulation()
    step = 0
    accident_time = 500
    accident_duration = 1000
    accident_edge = "386286298#3"
    
    try:
        while step < 2000:
            traci.simulationStep()
            
            if step == accident_time:
                print(f"Initiating accident at step {step}")
                simulate_accident(accident_edge)
            
            if step == accident_time + accident_duration:
                print(f"Clearing accident at step {step}")
                remove_accident(accident_edge)
            
            if step % 100 == 0:
                print(f"Simulation step: {step}")
                
            step += 1
            
    except Exception as e:
        print(f"Simulation error: {e}")
    finally:
        try:
            traci.close()
            print("Simulation ended")
        except:
            pass

if __name__ == "__main__":
    run_simulation()