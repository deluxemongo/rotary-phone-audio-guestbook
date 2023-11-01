#! /usr/bin/env python3

import audioInterface
import os
import yaml
import sys
import RPi.GPIO as GPIO

from datetime import datetime
from gpiozero import Button
from signal import pause
from pydub import AudioSegment
from pydub.playback import play
from random2 import choice
from glob import glob

try:
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError as e:
    print(
        f"Could not find the config.yaml file. FileNotFoundError: {e}. Check config location and retry."
    )
    sys.exit(1)

hook = Button(config["hook_gpio"])
led = config["led_gpio"]
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)


def off_hook() -> None:
    GPIO.output(led,GPIO.LOW)
    print("LED off")
    print("Phone off hook, ready to begin!")
    audio_interface = audioInterface.AudioInterface(config, hook)

    # random voicemessage
    random_voicemessage = choice(glob('sounds/*voicemessage*.wav'))
    print("Selected" + random_voicemessage.lstrip("sounds/") + "to play.")
    
    # playback voice message through speaker
    print("Playing voicemail message...")
    play(
        AudioSegment.from_wav(
            os.path.dirname(os.path.abspath(config["source_file"]))
            + "/" + random_voicemessage
        )
        #- config["playback_reduction"]
        + config["playback_increase"]
    )

    # start recording beep
    print("Playing beep...")
    play(
        AudioSegment.from_wav(
            os.path.dirname(os.path.abspath(config["source_file"])) + "/sounds/beep.wav"
        )
        #- config["beep_reduction"]
        + config["beep_increase"]
    )

    # now, while phone is off the hook, record audio from the microphone
    print("recording")
    audio_interface.record()
    audio_interface.stop()
    cur_dt = datetime.now().isoformat()
    output_file = (
        os.path.dirname(os.path.abspath(config["source_file"]))
        + "/recordings/"
        + cur_dt
    )
    audio_interface.close(output_file + ".wav")
    print("Finished recording")
    recording = AudioSegment.from_file(output_file + ".wav")
    recording.export(
        output_file + ".mp3", format="mp3"
    )
    print("Converted to mp3")
    #os.remove(output_file + ".wav")
    #print("Removed original wav-file")
    print("Finished!")


def on_hook() -> None:
    GPIO.output(led,GPIO.HIGH)
    print("LED on")
    print("Phone on hook.\nSleeping...")


def main():
    hook.when_pressed = off_hook
    hook.when_released = on_hook
    pause()


if __name__ == "__main__":
    main()
