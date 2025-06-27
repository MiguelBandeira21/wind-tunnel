import windtunnel
import inductiva


project = inductiva.projects.Project(
   name="UAV_dataset")

# Allocate cloud machine
cloud_machine = inductiva.resources.MachineGroup(
   provider="GCP",
   machine_type="c2d-highcpu-32",
   spot=True
)

tasks = []
DATASET_SIZE = 41
alpha = -20 # Angle of attack

for i in range(DATASET_SIZE):
    
    # Create wind tunnel object
    wind_tunnel = windtunnel.WindTunnel(dimensions=(20,10,8))

    # Set the object in the windtunnel
    wind_tunnel.set_object(
        object_path="assets/orientedUAV.obj",
        rotate_z_degrees=0,
        rotate_y_degrees=alpha,
        translate=[0,0,2],
        normalize=False,
        center=True,
    )

    # Display the Windtunnel with the object
    wind_tunnel.display()

    print("Starting UAV Simulation")
    # Submit a simulation task
    task = wind_tunnel.simulate(wind_speed_ms=20,
                                num_iterations=50,
                                resolution=3, 
                                machine_group_name=cloud_machine.name)
    
    project.add_task(task)
    
    task.wait() 

    alpha += 1
    
    
   
for task, alpha in tasks:
    output = task.get_output()  # waits until done
    task.set_metadata({"angle_of_attack": str(alpha)})

project.wait()
cloud_machine.terminate()

