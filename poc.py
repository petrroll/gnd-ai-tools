import fire
import unidecode
import re

from tts import DummyVoice
from stt import Orthograph
from rnnGen import RnnGen


def strip_diacritics(s):
    return unidecode.unidecode(s)

def clean_text(text):
    in_text = text
    if in_text is not None:
        # Apply text transformations to ensure that
        # the transcribed text belongs to a character set
        # which is a subset of the char-rnn's vocabulary
        in_text = strip_diacritics(in_text)
        in_text = in_text.lower()
    else:
        in_text = ""

    return in_text


def main(char_rnn_ckpt_dir='charrnn/save',
        input_device=None,
        lang='cs-CZ',
        next_key=None,
        exit_key='ananas',
        sample_length=100,
        say_primed=True):

    voice = DummyVoice(lang=lang)
    ortho = Orthograph(lang=lang, input_device=input_device)
    char_rnn = RnnGen(char_rnn_ckpt_dir=char_rnn_ckpt_dir, sample_length=sample_length)

    while True:

        # Get transcripts until `next_key` is said / just one final transcript
        transcripts = []
        for phrase, _ in ortho.produce():       # produce returns tuple, discart the `.is_final`
            clean_phrase = clean_text(phrase)
            transcripts.append(clean_phrase)
            print("<<<:", clean_phrase)

            if next_key is None:                # Don't wait on next_key, continue generate response immediately
                break       
            elif next_key in clean_phrase: 
                transcripts = transcripts[:-1]      # remove the phrase with next_key
                break
            elif exit_key in clean_phrase:
                exit()

        in_text =  '. '.join(transcripts)

        # Produce rnn output for in_text
        out_text = char_rnn.produce(in_text)
        if not say_primed:
            out_text = out_text[len(in_text):]

        # Send out_text to TTS
        print(">>>: ", out_text)
        voice.consume(out_text)

        

if __name__ == "__main__":
    fire.Fire(main)
