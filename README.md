

### Setup
- Run `make prereq-apt` to install apt-dependencies
- Run `make env` to setup python virtual environment / `pip3 install -r requirements.txt` to setup global 

#### Setup STT:
- Set authentication for Google Cloud (e.g. `export GOOGLE_APPLICATION_CREDENTIALS=<path/to/credentials.json>` or [any other possible way](https://cloud.google.com/docs/authentication/production)).


### Architecture
- All modules either consume / produce data / produce data based on input.
- Producers (STT) are python generators that yield data
- Consumers have `Consume(data)` method that can optionally return (producer based on input e.g. charnn) 

### Modules:

#### stt:
- pure producer `Orthograph(lang, input_device, only_final)`
  - `produce()` -> generator that yields `(transcript, result.is_final)`
- The TTS and STT language is set by `--lang <l>` and defaults to `cs-CZ` (`en-US` works too).
- The exit-keyword is set by `--exit_key <k>` and defaults to *ananas*.
- You can choose to get non-final transcripts as well via `--only_final False`
- Standalone: Listens and transcribes audio to standart output

#### rnnGen: 
- consumer/producer `RnnGen(char_rnn_ckpt_dir, sample_length, remove_prime)`
- `produce(input)` -> generated text primed by input
  - `--remove_prime` specifies whether the input is supposed to be cut from the beginning of the result
- The directory containing a pretrained char-rnn model is set by `--char_rnn_ckpt_dir <d>` and defaults to `charrnn/save` (which by default doesn't exist, so make sure you either provide it or specify a valid path).

#### tts:
- consumer `DummyVoice(lang)`
- `consume(input)` -> TTS plays audio of `input` string
- The TTS and STT language is set by `--lang <l>` and defaults to `cs-CZ` (`en-US` works too).
- Notes: for windows `pip install pypiwin32`; for linux just `make`

### Credits: 
- [Google Speech API samples](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/speech/microphone)
- @sherjilozair[/char-rnn-tensorflow](https://github.com/sherjilozair/char-rnn-tensorflow/blob/master/model.py)




### mets (Metastasis)
---
#### Setup

1. `apt-get install portaudio19-dev`
2. `pip3 install -r requirements.txt`
3. Make sure you have a speech engine driver installed (e.g. by `apt-get install espeak`).
5. Run `python3 poc.py  <args>`

#### Running

Atm, `poc.py` consists of a loop - you may speak, and what you say is transcribed trough GC's Speech API into text, until a keyword is not recognized. At this point, the connection to GC is closed and the transcribed text (except the keyword) is forwarded to the running char-rnn language model. The generated text from the language model is spoken trough a text-to-speech interface.
To exit the application, besides `Ctrl-C`-ing it, you can say the special killing keyword.


#### Notes

`poc.py` accepts the following optional arguments:
* The move-on-keyword is set by `--next_key <k>` and defaults to *figaro*.
* The directory containing a pretrained char-rnn model is set by `--char_rnn_ckpt_dir <d>` and defaults to `charrnn/save` (which by default doesn't exist, so make sure you either provide it or specify a valid path).
* After setting the patience flag with `--patient True`, the program will wait for you to hit Enter, before making new connections to the Speech API.
* By default, the text spoken includes the primed text (the transcription) and the generated text. To say only what has been generated, set `--say_primed False`.

You may like to choose the keywords based on the language used.

Make sure, that the speech transcriptions are in a character set, which belongs to the char-rnn model's vocabulary.