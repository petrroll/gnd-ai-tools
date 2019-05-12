""" Text to Speech """

import pyttsx3
import fire

class Voice():
    def __init__(self):
        pass

    def consume(self, str):
        pass

class DummyVoice(Voice):
    def __init__(self, lang='cs-CZ', rate=100):
        """
            Args:
                lang: cs-CZ or en-US
                rate: words per minute
        """
        self._engine = pyttsx3.init()
        if lang == 'cs-CZ':
            self._engine.setProperty('voice', 'czech')
        elif lang == 'en-US':
            self._engine.setProperty('voice', 'english')
        self._engine.setProperty('rate', rate)

    def consume(self, str):
        self._engine.say(str)
        self._engine.runAndWait()

def main(lang='cs-CZ', exit_key='ananas'):
    voice = DummyVoice(lang)
    text_in = input()

    while not exit_key in text_in:
        voice.consume(text_in)
        text_in = input()


if __name__ == "__main__":
    fire.Fire(main)
