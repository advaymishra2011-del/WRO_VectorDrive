# Electromechanical Schematics
The main wiring diagrams and power distribution of components used

**See Circuit Overview for components and distribution**

## Electronics and Component Selection

The electronics system was designed around three main requirements: real-time autonomous control, reliable sensor perception, and low mass and power consumption. The robot uses a Raspberry Pi 5 as the high-level computing platform and a Raspberry Pi Pico as the low-level controller. This separation allows computationally intensive perception and decision-making to run on the Pi while maintaining reliable, deterministic control of the motor, steering servo, encoder and collision sensors through the Pico.

# Computing and Control

The Raspberry Pi 5 was selected as the main computer because the robot requires real-time camera processing alongside multiple sensor inputs. The Camera Module 3 is used for computer vision, while the five VL53L0X sensors, BNO085 IMU and TCS34725 colour sensor provide additional environmental and vehicle-state information. A Pi Zero 2 W was considered because of its smaller size and lower power consumption, but the Pi 5 provides substantially greater computational headroom for image processing and sensor fusion. We therefore accepted the additional mass and power consumption of the Pi 5 in exchange for greater processing capability and reliability.

The Raspberry Pi Pico is used as a dedicated low-level controller. It controls the DRV8833 motor driver and MG90S steering servo, reads the N20 motor encoder and monitors the four collision switches. This division prevents the Linux operating system on the Pi 5 from directly controlling time-critical functions and allows motor and steering control to remain responsive even while the Pi is processing camera data. Communication between the two computers is performed using UART.

# Drive System

The robot uses a GA12-N20 6 V, 300 RPM geared DC motor with an encoder as its drive motor. The motor was selected because its small size and gearbox provide a suitable compromise between speed, torque and packaging requirements for the compact chassis. The encoder additionally provides feedback about motor rotation, allowing the Pico to measure wheel speed and implement closed-loop control rather than relying only on a predetermined PWM value.

The theoretical linear speed of the robot is determined by v=πDN/60 where D is the wheel diameter and N is the motor speed in RPM. Although the motor is rated at approximately 300 RPM at its nominal voltage, the actual vehicle speed will be lower under load. We therefore intend to determine the optimum operating PWM experimentally by measuring acceleration, maximum stable speed and cornering behaviour rather than simply operating the motor at maximum speed. This allows us to prioritise stable lap completion over maximum theoretical speed.

The motor is controlled using a DRV8833 dual H-bridge motor driver. The driver allows the Pico to control motor direction and speed using PWM while supplying the significantly higher current required by the motor. The DRV8833 was chosen instead of larger motor drivers such as the L298N because it is considerably more compact and efficient, making it better suited to a small autonomous vehicle.

The MG90S metal-geared servo is used for steering. A servo was selected instead of an additional drive motor because it provides direct and repeatable control of the steering angle while remaining compact. The Pico generates the servo PWM signal, allowing steering control to remain independent of the computational workload on the Raspberry Pi.

# Power System

The robot is powered by a 7.4 V nominal, 1500 mAh, 25C 2S LiPo battery. A 2S battery was selected because it provides sufficient energy and current capability while remaining relatively compact and lightweight. Its nominal stored energy is approximately

E=VQ=(7.4)(1.5)=11.1 Wh.

The battery is connected to a regulated 5 V supply, which powers the Raspberry Pi 5, Raspberry Pi Pico and MG90S servo. The same regulated 5 V rail is supplied to the DRV8833 motor driver, allowing the N20 motor to operate at approximately 5 V. Operating the 6 V motor at 5 V provides a conservative operating voltage and reduces the need for an additional motor-voltage regulator, simplifying the power system and reducing weight and wiring.

The power system was designed so that the motor current does not pass through the Raspberry Pi or Pico. The DRV8833 acts as the power interface between the Pico's control signals and the motor.

# Distance Sensing

Five VL53L0X time-of-flight sensors are used for distance measurement. Four are positioned toward the front of the robot and one toward the rear. The four front sensors provide multiple measurements across the robot's field of travel, allowing the robot to estimate its position relative to walls and other objects rather than relying on a single distance measurement. The rear sensor provides information during reversing and rear-boundary interactions.

The VL53L0X sensors communicate using I²C. Since multiple identical VL53L0X sensors normally share the same I²C address, a CJMCU TCA9548A 8-channel I²C multiplexer is used. Each sensor is connected to a separate TCA9548A channel, allowing all five sensors to be independently addressed without modifying their hardware addresses. Only five of the eight available channels are therefore required, leaving additional channels available for future expansion.

# Orientation and Colour Sensing

A BNO085 IMU is included to provide information about the robot's orientation and motion. IMU measurements can complement wheel-encoder and camera data, particularly during turns, allowing the robot to estimate changes in heading and improve the consistency of its movement.

A TCS34725 RGB colour sensor is used as a dedicated colour measurement device. A separate colour sensor was selected rather than relying entirely on the camera because it provides direct RGB measurements with low computational overhead. The camera provides spatial and visual information, while the TCS34725 provides a simple independent colour measurement. This gives the robot multiple sensing methods rather than relying on a single sensor.

# Camera and Computer Vision

The Raspberry Pi Camera Module 3 is the primary visual sensor. It provides the image data required for computer-vision algorithms running on the Raspberry Pi 5. The camera allows the robot to detect and analyse features of the track and surrounding environment that cannot be represented by a single distance measurement.

A suitable 15-pin to 22-pin camera FPC cable is used to connect the Camera Module 3 to the Raspberry Pi 5, since the two devices use different physical connector formats.

# Collision Detection

Four NO/NC/C mechanical touch sensors are used as a supplementary collision-detection system. The switches provide a simple digital indication of physical contact and therefore require very little processing or electrical power.

For collision detection, only the Common (C) and Normally Open (NO) terminals are required. The NC terminal is left unused. Each switch is connected to a Pico GPIO using an internal pull-up resistor, producing a simple HIGH/LOW signal. The four sensors allow the robot to determine approximately which region of the vehicle has made contact and provide a backup mechanism for responding to unexpected physical collisions.
