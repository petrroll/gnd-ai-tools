import fire

from tts import DummyVoice
from wrappers.SocketReader import SocketReader

def main(lang='cs-CZ',host='127.0.0.1', port=4444, sep='\n'):

    voice = DummyVoice(lang=lang)
    reader = SocketReader(host, port, sep)

    for msg in reader.produce():
        voice.consume(msg)

if __name__ == "__main__":
    fire.Fire(main)
