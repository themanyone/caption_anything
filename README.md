# Caption Anything

<img src="img/ss.png" width="300" align="right">

Caption, translate, or optionally record, whatever audio/video is playing through the speakers, or from the microphone. Privacy-focused, offline, real-time captions using your video card and [whisper-jax](https://github.com/sanchit-gandhi/whisper-jax/).

It is especially handy for people with hearing or memory loss, or people who speak another language, to caption and record calls. The maker of this app uses it to make sense of informational videos made with a strong accent. Captions can be saved in a variety of formats. The saved data could even be corrected and used to train another AI.

## Notices

These apps take upwards of 2Gb of video memory for the AI. This is not designed as a dictation app. [Try my other app for dictation.](https://github.com/themanyone/whisper_dictation) It is not a full-featured recording app either. Although it might be useful to record from music sites that otherwise discourage recording. If you don't need captions and just want to record and edit audio, try [audacity](https://sourceforge.net/projects/audacity/).

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the included GNU General Public License for more details.

## Usage

If you want to record and/or caption **both** sides of a conversation, echo the mic to the output channel first. You could do that via gstreamer. **WARNING.** This will cause unwanted feedback if your volume is up too high!

```
gst-launch-1.0 -v autoaudiosrc ! autoaudiosink
```

Set up your inputs and outputs using your favorite mixer program. Then, fire up `caption_anything.py`, choose the monitor device, which might look like `Monitor of Built-In Analog Stereo`. And do your recording/captioning from there. Be aware that there might be laws that require consent for recording and/or publishing conversations and copyrighted content.

## Requirements

Install [whisper-jax and requirements]([WhisperX and requirements](https://github.com/sanchit-gandhi/whisper-jax). Get whisper-jax working first, by trying out some of their examples.

Install more requirements. Not tested or guaranteed to work yet. You might need to edit the requirements for your setup.

```
# activate conda or venv
python3 -m venv .venv
source .venv/bin/activate
pip3 -r requirements.txt
```

## Adjustable settings

It's python, so feel free to edit `caption_anything.py`. You could change sample_rate to 22050, and 1 channel for recordings if all you want to save space with voice recordings. You could change the task to "translate" if you prefer your captions to translate from another language.

## Generate captions via the network

There are already plenty of apps for that. This app took [this one](https://github.com/sanchit-gandhi/whisper-jax/blob/main/app/app.py) and adapted it to work offline and locally, in real-time, on a single machine.

## Issues

**GPU memory usage.** According to a post by [sanchit-gandhi](https://github.com/sanchit-gandhi/whisper-jax/issues/7#issuecomment-1531124418), JAX using 90% of GPU RAM is probably unnecessary, but intended to prevent fragmentation. You can disable that with an environment variable, e.g. `XLA_PYTHON_CLIENT_PREALLOCATE=false ./caption_anything.py`.

You can also reduce memory footprint by using a smaller language model for whisper-jax.

You can monitor JAX memory usage with [jax-smi](https://github.com/ayaka14732/jax-smi), `nvidia-smi`, or by installing the bloated, GreenWithEnvy (gwe) for Nvidia cards which does the same thing with a graphical interface.

This is a fairly new project. There are bound to be more issues. Share them on the [issues section on GitHub](https://github.com/themanyone/caption_anything/issuess). Or fork the project, create a new branch with proposed changes. And submit a pull request.

### Thanks for trying out Caption Anything.

Browse Themanyone
- GitHub https://github.com/themanyone
- YouTube https://www.youtube.com/themanyone
- Mastodon https://mastodon.social/@themanyone
- Linkedin https://www.linkedin.com/in/henry-kroll-iii-93860426/
- [TheNerdShow.com](http://thenerdshow.com/)