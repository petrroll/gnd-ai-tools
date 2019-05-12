import fire
from lm import CharRNNWrapper

class RnnGen():
    def __init__(self, char_rnn_ckpt_dir='charrnn/save', sample_length=20, remove_prime=True):
        self.sample_length = sample_length
        self.char_rnn = CharRNNWrapper(ckpt_dir=char_rnn_ckpt_dir)
        self.remove_prime = remove_prime

    def produce(self, input):
        """
            Returns:
                Generated text primed by input. Depending on remove_prime from init prefixed by the input.
        """
        safe_input = input or " "
        generated =  self.char_rnn.sample(prime_text=safe_input, sample_len=self.sample_length, sampling_strategy=1)
        return generated[min(len(input), len(generated)):] if self.remove_prime else generated


def main(char_rnn_ckpt_dir='charrnn/save',
        sample_length=20, remove_prime=True, exit_key='ananas'):

    gen = RnnGen(char_rnn_ckpt_dir, sample_length, remove_prime)
    text_in = input()

    while not exit_key in text_in:
        print(gen.produce(text_in))
        text_in = input()

if __name__ == "__main__":
    fire.Fire(main)
