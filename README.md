# Thanks to nickpourazima for his work and initial creation of the code

# Rotary Phone Audio Guestbook

- [Rotary Phone Audio Guestbook](#rotary-phone-audio-guestbook)
  - [Background](#background)
  - [Materials](#materials)
  - [Hardware](#hardware)
    - [Wiring](#wiring)
      - [Hook](#hook)
      - [Phone Cord](#phone-cord)
  - [Software](#software)
    - [Dependencies](#dependencies)
    - [Config](#config)
    - [AudioInterface Class](#audiointerface-class)
      - [audioGuestBook systemctl service](#audioguestbook-systemctl-service)
    - [Operation Mode 1: audioGuestBook](#operation-mode-1-audioguestbook)

This project transforms a rotary phone/modern phones into a voice recorder for use at special events (i.e. wedding audio guestbook, etc.).

## Background

I was inspired by the code of nickpourazima and decided to fork his project and change some code for my own needs.

## Materials

| Part|Notes|Quantity|Cost|
| - | - | - | - |
| [vintage phone](https://www.ebay.de/itm/404293086338?mkcid=16&mkevt=1&mkrid=707-127634-2357-0&ssspo=ctzullghs8u&sssrc=2047675&ssuid=&widget_ver=artemis&media=COPY) | Decided to buy a phone in vintage look, old rotarys in good condition were to expesive | 1 | 40 EUR |
| [raspberry pi zero (2) (with gpio)](https://www.raspberrypi.com/products/raspberry-pi-zero/) | I wanted to put the pi into the the phone, but you can use any pi you want | 1 | 15 - 30 EUR |
| [micro SD card] | Any high capacity/throughput micro SD card that is rpi compatible | 1 | 5 - 20 EUR |
| [USB Audio Adapter](https://www.adafruit.com/product/1475) | To wire the mic and speaker  | 1 | 5 EUR |
| [USB OTG Host Cable - MicroB OTG male to A female](https://www.adafruit.com/product/1099) | | 1 | 3 EUR |
| --- | **--- If you don't want to solder anything ---** | --- | --- |
| [3.5mm Male to Screw Terminal Connector](https://www.parts-express.com/3.5mm-Male-to-Screw-Terminal-Connector-090-110?quantity=1&utm_source=google&utm_medium=cpc&utm_campaign=18395892906&utm_content=145242146127&gadid=623430178298&gclid=CjwKCAiAioifBhAXEiwApzCztl7aVb18WP4hDxnlQUCHsb62oIcnduFCSCbn9LFkZovYTQdr6omb3RoCD_gQAvD_BwE) | If you do not want to wire the cable directly to the audio adapter, use two of these | 2 | 4 EUR |
| --- | **--- If replacing the built-it microphone ---** | --- | --- |
| [LavMic](https://www.amazon.com/dp/B01N6P80OQ?ref=nb_sb_ss_w_as-reorder-t1_ypp_rep_k3_1_9&amp=&crid=15WZEWMZ17EM9&amp=&sprefix=saramonic) | Optional: if you'd like to replace the carbon microphone. This is an omnidirectional lavalier mic and outputs via a 3.5mm TRS | 1 | 30 EUR |

## Hardware

### Wiring

#### Hook

- Use multimeter to do a continuity check to find out which pins control the hook:
  
#### Phone Cord

- The wires from the handset cord need to be connected to the USB audio interface directly or with the connectors

- Use this ALSA command from the command line to test if the mic is working on the rpi before you set up the rotary phone: `aplay -l`
  - You might have a different hardware mapping than I did, in which case you would change the `alsa_hw_mapping` in the [config.yaml](config.yaml).
  - [Here's](https://superuser.com/questions/53957/what-do-alsa-devices-like-hw0-0-mean-how-do-i-figure-out-which-to-use) a good reference to device selection.
  - You can also check [this](https://stackoverflow.com/questions/32838279/getting-list-of-audio-input-devices-in-python) from Python.

## Software
### Dependencies

- `sudo apt update` 
- `sudo apt-get install python3-scipy ffmpeg python3-pyaudio vim git python3-pip python3-random2` 
- `sudo apt full-upgrade -y && sudo apt autoremove -y` 

- `pip3 install -r requirements.txt` or pip install each manually:
  - [GPIOZero](https://gpiozero.readthedocs.io)
  - [Pydub](http://pydub.com/)
  - [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
  - [PyYAML](https://pyyaml.org/)
 
- Maybe you have to set your USB Audio Device as Default. This can be done by `sudo raspi-config` in the Interface Options

### [Config](config.yaml)

- This file allows you to customize your own set up (edit rpi pins, audio reduction/increase, alsa mapping, etc), modify the yaml as necessary.

- For GPIO mapping, refer to the wiring diagram specific to your rpi:
  ![image](images/rpi_GPIO.png)

### [AudioInterface Class](audioInterface.py)

- Utilizes pydub and pyaudio extensively.
- Houses the main playback/record logic

#### [audioGuestBook systemctl service](/audioGuestBook.service)

This service starts the python script on boot. Place it in the `/etc/systemd/system` directory. Change the lines "WorkingDirectory", "Username" and "ExecStart" to your needs, before you copy the file.

```sh
systemctl enable audioGuestBook.service
systemctl start audioGuestBook.service
```

### Operation Mode [audioGuestBook](/audioGuestBook.py)-files

- This is the main operation mode of the device.
- There are two callbacks in main which poll the gpio pins for the specified activity (hook depressed, hook released).
- Comment in/out the lines for playback/beep_reduction/increase
- Once triggered the appropriate function is called.
- On hook (depressed)
  - Nothing happens
- Off hook (released)
  - Plays back one of your own welcome message located in `/sounds/*voicemail*.wav` followed by the beep indicating ready to record.
  - Begins recording the guests voice message.
  - Guest hangs up, recording is stopped and stored to the `/recordings/` directory.
  - wav files will be converted into mp3
