# Birdhouse

This is fun project to create small birdhouse, attached with motion sensor and
cam. When there is motion detected, the cam shoots a picture and transmits it
via telegram.

When there is continuous movement, pictures are taken every few seconds (depends on
the hardware) until there is no further movement within 10s. After that, the
images are converted via imagemagick to an animated gif and transmitted once to
every subscriber.

Following chat commands are available:

- /sub     - Subscribe to updates
- /unsub   - Unsubscribe from updates
- /pause   - Pause motion tracking
- /unpause - Unpause motion tracking
- /pic     - Take a picture
- /stat    - Show status
- /rest    - Restart
- /die     - Shutdown

# Parts list

- 1x Raspberry Pi Zero W
- 1x HC SR501 Pir motion sensor
- 1x Pi cam
- 1x Cam cable for Pi Zero
- A bit of wiring, tin, psu  and filament

# Print settings

Nothing special, model can be printed on the back in one go.

# Prototype

![Prototype 1](pictures/prototype1.jpg?raw=true "Prototype 1")
![Prototype 2](pictures/prototype2.jpg?raw=true "Prototype 2")
![Prototype 3](pictures/prototype3.jpg?raw=true "Prototype 3")

# Model

![Model](pictures/3dmodel.png?raw=true "Model")

# Cam

![Cam](pictures/cam1.jpg?raw=true "Cam")
![Cam](pictures/cam2.jpg?raw=true "Cam")
![Cam](pictures/cam3.jpg?raw=true "Cam")
![Cam](pictures/cam4.jpg?raw=true "Cam")

# Animation

And an example animation:

![Animation](pictures/anim.gif?raw=true "Animation")
