# caption_anything

<img src="wyh.png">

Caption or translate whatever is playing through the speakers, or from the microphone. Also record audio and/or create captions as you record calls.

If you want to record **both** sides of the conversation, you will have to echo the mic to the output channel first. You could do that via gstreamer. 

**WARNING.** This will cause unwanted feedback if your volume is up too high!

```
gst-launch-1.0 -v autoaudiosrc ! autoaudiosink
```

Or set up your inputs and outputs using your favorite mixer program. Then, fire up `caption_anything`, choose the monitor device, which might look like "Monitor of Built-In Analog Stereo". And do your recording/captioning from there.

## Requirements

Install [whisper-jax and requirements]([WhisperX and requirements](https://github.com/sanchit-gandhi/whisper-jax). Get whisper-jax working first, by trying out some of their examples.

Install more requirements. Not tested or guaranteed to work yet. You might need to edit the requirements for your setup.

```
pip3 -r requirements.txt
```

## Adjustable settings

It's python, so feel free to adjust anything. You could change sample_rate to 22050, and 1 channel for recordings if all you want to save space with voice recordings. You could change the task to "translate" if you want your captions to translate from another language.