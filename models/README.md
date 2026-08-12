# 3D Models
**Overview**: Small, 11x10cm layer style design

### Bottom Layer
**Front**: Parallel Ackerman Style steering setup controlled with parallel motor control
**Rear**: Simple spur gear from motor to shaft that connects to both wheels
**Wheels**: TPA95 Filament tires and PLA rims custom designed and printed

### Mid-Lower Layer
**Battery**: Battery at center to ensure no divergence of center of mass
**Wiring Space**: Taking advantage of gear mounts and extra space to create small wiring pipes to for the extra overcrowded wires

### Surface
**Mounts**: Touch sensor, ToF and Camera mounts on sides
**Components**: Main perfboard with IMU, Pico, Multiplexer and motor driver
**Pi5**: Mounted above the perfboard to ensure balance and optimize usage of space

## Battery Placement and Wiring
### Battery Placement

The 2S 1500 mAh LiPo battery is positioned near the centre of the chassis.

This was done primarily to keep the centre of mass close to the geometric centre of the robot. Placing the relatively heavy battery at one end would increase the moment of inertia about the opposite end and could produce different handling characteristics when accelerating, braking or turning.

Central battery placement also helps distribute the load between the front and rear axles.

The battery is also positioned low in the chassis, lowering the centre of gravity and reducing the tendency of the robot to become unstable during rapid steering changes.

### Wiring Management

The large number of sensors creates a significant wiring requirement, particularly because the robot contains:

- Five VL53L0X sensors
- BNO085
- TCS34725
- Four collision sensors
- Motor encoder
- Servo
- Motor
- Pi 5
- Pico
- Camera

Instead of allowing these wires to occupy the main interior volume of the robot, small wiring channels are integrated into the chassis around the gear mounts and other unused structural spaces.

This serves two purposes:

It makes the wiring more compact and protected from the drivetrain.
It prevents loose wires from interfering with the steering and gears.

The wiring channels therefore allow the same chassis volume to perform both structural and cable-management functions.
