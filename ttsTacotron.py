""" Text to Speech """

#
#   REMARKS: Works only for `Tacotron` model, not `WaveNet` / `Tacotron-2`.
#

import argparse
import fire
import sys
import os

sys.path.insert(1, 'Tacotron-2')
sys.path.insert(1, 'Tacotron-2/tacotron')

from infolog import log
from warnings import warn

import tensorflow as tf
from hparams import hparams, hparams_debug_string
from tacotron.synthesizer import Synthesizer

class Voice():
	def __init__(self, args):
		pass

	def consume(self, str):
		pass


class TacotronVoice(Voice):

	def __init__(self, args):
		taco_checkpoint, _, hparams = self.prepare_run(args)
		
		self.args = args
		self.load_checkpoint(args, hparams, taco_checkpoint)

	def prepare_run(self, args):
		# modified ./Tacotron-2/synthesize.py:prepare_run

		modified_hp = hparams.parse(args.hparams)
		os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

		run_name = args.name or args.tacotron_name or args.model
		taco_checkpoint = os.path.join('Tacotron-2', 'logs-' + run_name, 'taco_' + args.checkpoint)

		run_name = args.name or args.wavenet_name or args.model
		wave_checkpoint = os.path.join('Tacotron-2', 'logs-' + run_name, 'wave_' + args.checkpoint)
		return taco_checkpoint, wave_checkpoint, modified_hp

	def load_checkpoint(self, args, hparams, checkpoint):
		# ./Tacotron-2/tacotron/synthesize.py:tacotron_synthesize
		output_dir = 'tacotron_' + args.output_dir

		try:
			checkpoint_path = tf.train.get_checkpoint_state(checkpoint).model_checkpoint_path
			log('loaded model at {}'.format(checkpoint_path))
		except:
			raise RuntimeError('Failed to load checkpoint at {}'.format(checkpoint))

		if hparams.tacotron_synthesis_batch_size < hparams.tacotron_num_gpus:
			raise ValueError('Defined synthesis batch size {} is smaller than minimum required {} (num_gpus)! Please verify your synthesis batch size 	choice.'.format(
				hparams.tacotron_synthesis_batch_size, hparams.tacotron_num_gpus))

		if hparams.tacotron_synthesis_batch_size % hparams.tacotron_num_gpus != 0:
			raise ValueError('Defined synthesis batch size {} is not a multiple of {} (num_gpus)! Please verify your synthesis batch size choice!'.format(
				hparams.tacotron_synthesis_batch_size, hparams.tacotron_num_gpus))

		# ./Tacotron-2/tacotron/synthesize.py:run_live
		log(hparams_debug_string())
		synth = Synthesizer()
		synth.load(checkpoint_path, hparams)

		self.model = synth

	def generate_fast(self, model, text):
		model.synthesize([text], None, None, None, None)

	def consume(self, strInput):
		self.generate_fast(self.model, strInput)

def main():

	# copied from ./Tacotron-2/synthesize.py
	accepted_modes = ['eval', 'synthesis', 'live']
	parser = argparse.ArgumentParser()
	parser.add_argument('--checkpoint', default='pretrained/', help='Path to model checkpoint')
	parser.add_argument('--hparams', default='tacotron_num_gpus=1,tacotron_batch_size=1,cleaners=transliteration_cleaners,predict_linear=False',
		help='Hyperparameter overrides as a comma-separated list of name=value pairs')
	parser.add_argument('--name', help='Name of logging directory if the two models were trained together.')
	parser.add_argument('--tacotron_name', help='Name of logging directory of Tacotron. If trained separately')
	parser.add_argument('--wavenet_name', help='Name of logging directory of WaveNet. If trained separately')
	parser.add_argument('--model', default='Tacotron')
	parser.add_argument('--input_dir', default='training_data/', help='folder to contain inputs sentences/targets')
	parser.add_argument('--mels_dir', default='tacotron_output/eval/', help='folder to contain mels to synthesize audio from using the Wavenet')
	parser.add_argument('--output_dir', default='output/', help='folder to contain synthesized mel spectrograms')
	parser.add_argument('--mode', default='eval', help='mode of run: can be one of {}'.format(accepted_modes))
	parser.add_argument('--GTA', default='False', help='Ground truth aligned synthesis, defaults to True, only considered in synthesis mode')
	parser.add_argument('--text_list', default='', help='Text file contains list of texts to be synthesized. Valid if mode=eval')
	parser.add_argument('--speaker_id', default=None, help='Defines the speakers ids to use when running standalone Wavenet on a folder of mels. this variable must be a comma-separated list of ids')
	parser.add_argument('--exit_key', default='ananas', help='Defines word that stops interactive loop.')

	args = parser.parse_args()

	accepted_models = ['Tacotron', 'WaveNet', 'Tacotron-2']

	if args.model not in accepted_models:
		raise ValueError('please enter a valid model to synthesize with: {}'.format(accepted_models))

	if args.mode not in accepted_modes:
		raise ValueError('accepted modes are: {}, found {}'.format(accepted_modes, args.mode))

	if args.mode == 'live' and args.model == 'Wavenet':
		raise RuntimeError('Wavenet vocoder cannot be tested live due to its slow generation. Live only works with Tacotron!')

	if args.GTA not in ('True', 'False'):
		raise ValueError('GTA option must be either True or False')

	if args.model == 'Tacotron-2':
		if args.mode == 'live':
			warn('Requested a live evaluation with Tacotron-2, Wavenet will not be used!')
		if args.mode == 'synthesis':
			raise ValueError('I don\'t recommend running WaveNet on entire dataset.. The world might end before the synthesis :) (only eval allowed)')
	
	if args.model != 'Tacotron':
		raise ValueError('TTS interactive adapter is available only for Tacotron model, not {}'.format(args.model))

	voice = TacotronVoice(args)
	text_in = input()

	while not args.exit_key in text_in:
		voice.consume(text_in)
		text_in = input()


if __name__ == "__main__":
	main()
