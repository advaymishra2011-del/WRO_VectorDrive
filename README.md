# Vector Drive
Documentation for team Vector Drive for WRO Future Engineers 2026

### The Team
**Members**: Kush Agarwal, Shourya Pushkarna, Advay Mishra

## Bot Overview
### How the bot works
**5-ToF system**: 
- 1 Front and 2 on both sides to view full ground and run basic PID to prevent wall collision
- 2 Rear on both ends but facing backwards: Assist while parallel parking and allow to (1) Align with the wall and (2) Measure accurate distance when making a pivot turn in parallel park and making up for innacurate measurement from one
**Touch Sensor**:
- Touch sensor on front and back both ends to see collision based on physical touch and prevent damage with wall collision
**Other driving components**:
- BNO085: IMU for perfect steering and making desired angles based on obstacles (Colour blocks)
- N20 300RPM motor: Can bear the load and is fast but not too fast such that it may be unncontrollable

### Structure
- Compact chasis structure and built to be small yet powerful: Just 11x10cm but storing 300+g of electronics components such as Pi5 for high speed processing
- Box like, built around battery size
- Simple parallel-ackerman style steering and spur gear rear wheel drive to minimize space and not overcomplicate



