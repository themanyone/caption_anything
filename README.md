# Caption Anything

<img src="img/ss.png" alt="example pic" title="Actual screenshot of app generating captions." width="300" align="right">

Caption, translate, or optionally record, whatever audio/video is playing through the speakers, or from the microphone. Privacy-focused, offline, real-time captions using your video card and [whisper-jax](https://github.com/sanchit-gandhi/whisper-jax/) or [whisper.cpp](https://github.com/ggerganov/whisper.cpp).

Originally made for watching educational videos, whose presenters had a strong accent. This app would be especially handy for people with hearing or memory loss. Or those who speak another language. It can be used to caption and record VOIP, Zoom, or Google voice calls as well. The caption display is delayed slightly, so if you miss something, "Run that by me again?" Just glance at the output. Captions are saved in a variety of formats along with the recording. The saved audio and transcripts could even be corrected and used as data collection to train a large language model (LLM) with additional languages and dialects.

## Notices

This is not designed for dictation. [Try my other app for that.](https://github.com/themanyone/whisper_dictation) It is not a full-featured recording app either. Although it might be useful to record karaoke. If you don't need captions and just want to record and edit audio, try [audacity](https://sourceforge.net/projects/audacity/).

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the included GNU General Public License for more details.

## Usage

If you want to record and/or caption **both** sides of a conversation, echo the mic to the output channel first. You could do that via gstreamer. **WARNING.** This *will* cause unwanted feedback if your volume is set too high. And the other party might hear echos.

```
gst-launch-1.0 -v autoaudiosrc ! autoaudiosink
```

Set up your inputs and outputs using your favorite mixer program. Then, fire up `caption_anything.py`, choose the monitor device, which might look like `Monitor of Built-In Analog Stereo`. And do your recording/captioning from there. Right-click on the title bar and choose "Always on top" to see captions over other apps. Be aware that there might be laws that require consent for recording and/or publishing conversations and copyrighted content.

## Requirements

GUI: `sudo dnf -y install gobject-introspection-devel python3-pygobject-dvel` (fedora) or others, try `sudo apt install libgirepository1.0-dev llvm14-dev`

Then skip down to **generate captions via the network** if you want to use accelerated `whisper.cpp`.

Set up your virtual environment and prepare some requirements for Whisper-JAX.
 
```
# activate conda or venv
python3 -m venv .venv
source .venv/bin/activate
pip3 -r requirements.txt
```

Install [whisper-jax and requirements](https://github.com/sanchit-gandhi/whisper-jax) and get whisper-jax working before making captions here. Try out some of their examples. Then edit `checkpoint = "openai/whisper-small.en"` in `tqdm_loader.py` to use your preferred language model.

## Adjustable settings

It's python, so feel free to edit `caption_anything.py`. You could change sample_rate to 22050, and 1 channel for recordings if all you want to save space with voice recordings. You could change the task to "translate" if you prefer your captions to translate from another language. If there is enough VRAM, choose a larger model for the pipeline, such as `openai/whisper-large-v2` for better translation results. The smaller models just don't have as much language ability.

Set `max_duration` if you want to record or caption more than 120 minutes at a time. This will of course use more memory.

The captions can be shown in whatever font, color, size and style you want. Edit `style.css`.

## Generate captions via the network

`Whisper.cpp.` We now have a [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) client, `caption_cpp_client.py`. The client connects to a running instance of Whisper.cpp server. `whisper.cpp` does some translation into the target language `-l`. If you want it to specialize in translation, add `--translate` flag. And choose a larger model. The tiny model works fine for English. Compile `whisper.cpp` with CUDA (or whatever AI acceleration hardware your platform provides) for best results.

**Fedora 42.** is not CUDA-supported. But we figured it out! You can install CUDA for Fedora 41, and build `whisper.cpp` by removing
compatability versions of gcc14, gcc14-c++, if installed. And sourcing gcc13-13.3.1-2.fc41.1 and gcc13-c++-13.3.1-2.fc41.1 rpms from
Fedora 41 repos [as described here](https://github.com/themanyone/whisper_dictation#Preparation).

```shell
pip3 install -r requirements-client.txt
whisper-server -l en -m models/ggml-tiny.en.bin --port 7777
```

There is also a client for a [whisper-jax server](https://github.com/sanchit-gandhi/whisper-jax/blob/main/app/app.py) running on your local network. Or any copy of it hosted on the internet. Launch `caption_client.py` to connect to that.

`caption_anything.py` repurposes code from the [whisper-jax server](https://github.com/sanchit-gandhi/whisper-jax/blob/main/app/app.py) to run a single-user instance of it in memory, so you don't have to launch any servers or have the overhead from multiple processes, which provide absolutely no benefit for a single user.

## JAX Issues

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
- Buy me a coffee https://buymeacoffee.com/isreality
- [TheNerdShow.com](http://thenerdshow.com/)

Copyright (C) 2024-2025 Henry Kroll III, www.thenerdshow.com.
See [LICENSE](LICENSE) for details.
