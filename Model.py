from eldr.models.autoencoder import *
from eldr.models.vae.train_torch import *
from eldr.train import train_ae
from eldr.data import *
from torch.utils.data import Dataset, DataLoader
from types import SimpleNamespace
import json
import os
import sys
from eldr.models.vae.utils import sample_reparameterize







class Model(object):
	def __init__(self, model, model_type):
		self.model = model
		self.model_type = model_type


	@classmethod
	def Initialize(cls, model_type, input_, pretrained_path=None):
		if model_type != 'autoencoder' and model_type != 'vae':
			sys.exit("model_type wrong, provide right model type from: [autoencoder, vae]")

		if model_type == 'autoencoder':
			if pretrained_path == None:
				"""
					Train the model and load the best model
				"""
				print("Wait, the model is in training...")
				#Load the config file for the autoencoder
				path = os.path.join('./configs', str(model_type) + '.json')
				config = json.load(open(path, 'r'))
				config = SimpleNamespace(**config)

				print(config)

				"""
				train the model and return the best model, for now 
				we have the training script. But we have to write the trainer class
				to work for every model
				"""
				model = train_ae(input_,\
						encoder_shape=config.encoder_shape,\
						output_dim=config.output_dim,\
						decoder_shape=config.decoder_shape,\
						learning_rate=config.learning_rate,\
				 		batch_size=config.batch_size,\
				 		min_epochs=config.min_epochs,\
				 		stopping_epochs=config.stopping_epochs,\
				 		tol=config.tol,\
				 		eval_freq=config.eval_freq)

			else:	
				#Use the pretrained model placed at the pretrained_path
				#for now the whole model is saved after training, so 
				#this doesn't require any args. Is this a better way to save?
				print("Loading the pretrained model...")
				model = torch.load(pretrained_path)

		if model_type == 'vae':
			if pretrained_path == None:
				pass

			else:
				print("Loading the pretrained model...")
				model = torch.load(pretrained_path, map_location=torch.device('cpu'))

		return cls(model, model_type)



	def Encode(self, input_):
		"""
			Encode the input_ into low dimensional representation
		"""
		recons = torch.empty(input_.shape[0], 2)
		self.model.eval()
		dl = DataLoader(Data(input_), batch_size = 1, shuffle = False)
		for i, batch in enumerate(dl,0):
				input = batch.float()
				if self.model_type != 'vae':
					recon = self.model.encoder(input)
					recons[i,:] = recon.data.view(-1,2)
				else:
					means, log_stds = self.model.encoder(input)
					recon = sample_reparameterize(means, torch.exp(log_stds))
					recons[i,:] = recon.data.view(-1,2)

			
		return recons

	def Encode_ones(self, input):
		     return self.model.encoder(input)