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

#### General:
- Each module can be run as CLI application for testing.

#### stt.py:
- Producer `Orthograph(lang, input_device, only_final)`.
- `produce()` -> generator that yields `(transcript, result.is_final)`
- `--lang <l>`: sets STT language, defaults to  to `cs-CZ` (`en-US` works too).
- `--only_final False`: controlls whether non-final transcripts are yielded as well (pause for a few seconds to obtain final transcript).
- `--exit_key <k>`: exit-keyword, defaults to *ananas* (only for CLI testing).

#### rnnGen.py: 
- Consumer `RnnGen(char_rnn_ckpt_dir, sample_length, remove_prime)`.
- `produce(input)` -> generates and immediately returns text primed by input.
- `--char_rnn_ckpt_dir <d>`: directory containing a pretrained char-rnn model, defaults to `charrnn/save` (which by default doesn't exist, so make sure you either provide it or specify a valid path).
- `--sample_length`: length of generated sequence.
- `--remove_prime`: controlls whether the input is supposed to be cut from the beginning of generated result.

#### tts.py:
- Consumer `DummyVoice(lang)`
- `consume(input)` -> TTS plays audio of `input` string.
- `--lang <l>`: sets TTS language, defaults to  to `cs-CZ` (`en-US` works too).
- Notes: for windows `pip install pypiwin32`; for linux just `make` (or see what it installs).

### Wrappers:

#### SocketReader.py:
- Producer `SocketReader(host, port, sep)`.
- `produce()` -> yields messages converted to UTF-8 string read from socket one by one, blocks until it gets a full message that ends by separator.
- `--host`: host for socket server, keep empty.
- `--port`: port for socket server.
- `--sep`: separator of messages.
- Notes: Acts as socket server.

#### SocketWriter.py:
- Consumer `SocketWriter(host, port, sep)`.
- `consume(msg)` -> sends msg through socket as UTF-8 encoded string suffixed by separator.
- `--host`: host of socket to connect to.
- `--port`: port for socket server.
- `--sep`: separator of messages.
- Notes: Acts as socket client.

### POCs:

#### poc.py
Atm, `poc.py` consists of a loop - you may speak, and what you say is transcribed through GC's Speech API into text, until a keyword is not recognized. At this point, the connection to GC is closed and the transcribed text (except the keyword) is forwarded to the running char-rnn language model. The generated text from the language model is spoken through a text-to-speech interface.

- Args for `stt.py`, `tts.py`, `rnnGen.py` apply
- `--next_key <k>`: move-on-keyword, defaults to *figaro*. If it's not set the RNN is immediately run on first final transcript.
- `--say_primed False`: By default, the text spoken includes the primed text (the transcription) and the generated text. To say only what has been generated, set this to false.
- Run `python3 poc.py  <args>`

You may like to choose the keywords based on the language used.

Make sure, that the speech transcriptions are in a character set, which belongs to the char-rnn model's vocabulary.

#### poc_socketTTS.py:
- PoC listening on socket (see `SocketReader.py` args) and sending messages to `tts.py` service (see its args). 
- Showcase of how to use modules & socketWrappers together. 


### Credits: 
- [Google Speech API samples](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/speech/microphone)
- @sherjilozair[/char-rnn-tensorflow](https://github.com/sherjilozair/char-rnn-tensorflow/blob/master/model.py)
- @gnd, @SamMichalik (loads of code was lifted from [previous repo](https://github.com/gnd/cancer-works
))


