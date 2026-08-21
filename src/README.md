# Software
**Overview**: 
- Use of PID and ToF assisted navigation to navigate the arena and Camera colour detection to create a good route for the bot
- Touch sensors in front-back left-right in case of collision
- 2 ToF in back to help align with the wall with error correction

## UART - Interconnected
Use of UART communication protocol by wiring TX--RX of Pico and Pi5 to communicate 
- **Pico:** Handles all motor movement and collects touch sensor data
- **Pi5:** Handles the CV and main processing, sending signals to pico to run motors at specific speeds and running the main algorithm
