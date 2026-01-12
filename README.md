# qShot

**qShot** is a flexible, and extensible camera capture and control application for the Raspberry Pi and its Camera Modules. Built with Python3, PyQt5 and Picamera2 it provides a decent graphical interface for live camera preview, access to camera controls, playback and file management.


---

## Prerequisites

### Hardware prerequisites:
Qshot may run on a Raspberry Pi 4, although I have not tested that. For hardware I would recommend a Pi 5 as minimum with as much memory as possible: ideally 16 Gb, minimum 8Gb.

I don't recommend running this app in a virtual environment. Building PyQt5 in a virtual environment can be a can of worms.
### Software prerequisites:
Requires PyQt5, Libcamera2 and Vlc (for playback). The simplest was to ensure these are present is to do a full install of Debian 12 (Bookworm) or Debian 13 (Trixie) as either of these operating systems will have included these three packages.

The only thing you will need to install is the vlc python library:


```bash
    sudo apt install python3-vlc
```


## Getting Started

From the applicationm folder:

```bash
    python3 main.py
```
If the app detects a camera in either of the Pi's 2 CSI slots then it will load. If two cameras are detected you will be prompted to choose one or the other (Although the Pi 5 and Picamera can accomodate 2 running camera instances the app is currently 1 camera only). If no camera are detected the app will let you know.

If you think you have a camera attached and it is not being recognised then it's probably worth referrring to: [the Raspberry Pi camera documentation](https://www.raspberrypi.com/documentation/accessories/camera.html#installing-a-raspberry-pi-camera)

You can check that a camera is attached by opening a terminal window aand running:

```bash
    rpicam-hello
```
This should open a window on your screen, display briefly the current camera view, then close the window.

## Documentation

1. [Prerequisites and Limitations](docs/prerequisites.md)  
2. [Getting Started](docs/getting_started.md)  
3. [Concepts and Facilities](docs/concepts.md)  
4. Different Supplied Components  
   - [Simple Still](docs/simple_still.md)
   - [Simple Video](docs/simple_video.md)
   - [Classifier](docs/classifier.md)
   - [Detector](docs/detector.md)
5. [Using the Autofocus](docs/autofocus.md)  
6. [Audio](docs/audio.md)  
7. [Zoom Control](docs/zoom_control.md)  
8. [Tour of Menus](docs/menus.md)  
9. [Comments on Individual Cameras](docs/cameras.md)  
10. [FAQ](docs/faq.md)  
11. [Tips and Tricks](docs/tips.md)


---


## License

MIT License

---

**qShot — A modern, Python-powered camera capture and control tool for Raspberry Pi.**
