# MIT License
# 
# Copyright (c) 2018
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy.random as npr

from datasets.AbstractDataset import AbstractDataset
from datasets.LandmarkDataset import LandmarkDataset
from datasets.SimpleFaceDataset import SimpleFaceDataset
from datasets.TensorFlowDataset import TensorFlowDataset
from nets.NetworkFactory import NetworkFactory

class SimpleDataset(AbstractDataset):

	__positive_ratio = 1
	__part_ratio = 1
	__negative_ratio = 3

	def __init__(self, network_name='PNet'):	
		AbstractDataset.__init__(self, network_name)	
	
	def _generate_landmark_samples(self, landmark_image_dir, landmark_file_name, minimum_face, target_root_dir):
		landmark_dataset = LandmarkDataset()		
		return(landmark_dataset.generate(landmark_image_dir, landmark_file_name, minimum_face, target_root_dir))
		
	def _generate_image_samples(self, annotation_image_dir, annotation_file_name, minimum_face, target_root_dir):
		wider_dataset = SimpleFaceDataset()		
		return(wider_dataset.generate_samples(annotation_image_dir, annotation_file_name, minimum_face, target_root_dir))

	def _generate_image_list(self, base_number_of_images, target_root_dir):
		positive_file = open(SimpleFaceDataset.positive_file_name(target_root_dir), 'r')
		positive_data = positive_file.readlines()

		part_file = open(SimpleFaceDataset.part_file_name(target_root_dir), 'r')
		part_data = part_file.readlines()

		negative_file = open(SimpleFaceDataset.negative_file_name(target_root_dir), 'r')
		negative_data = negative_file.readlines()

		landmark_file = open(LandmarkDataset.landmark_file_name(target_root_dir), 'r')
		landmark_data = landmark_file.readlines()

		image_list_file = open(self._image_list_file_name(target_root_dir), 'w')

    		if(len(negative_data) > base_number_of_images * SimpleDataset.__negative_ratio ):
        		negative_number_of_images = npr.choice(len(negative_data), size=base_number_of_images * SimpleDataset.__negative_ratio, replace=True)
    		else:
        		negative_number_of_images = npr.choice(len(negative_data), size=len(negative_data), replace=True)

    		positive_number_of_images = npr.choice(len(positive_data), size=base_number_of_images * SimpleDataset.__positive_ratio, replace=True)
    		part_number_of_images = npr.choice(len(part_data), size=base_number_of_images * SimpleDataset.__part_ratio, replace=True)

    		for i in positive_number_of_images:
        		image_list_file.write(positive_data[i])
    		for i in negative_number_of_images:
        		image_list_file.write(negative_data[i])
    		for i in part_number_of_images:
        		image_list_file.write(part_data[i])

    		for item in landmark_data:
        		image_list_file.write(item)

		return(True)

	def _generate_dataset(self, target_root_dir):
		tensorflow_dataset = TensorFlowDataset()
		if(not tensorflow_dataset.generate(self._image_list_file_name(target_root_dir), target_root_dir, 'image_list')):
			return(False) 

		return(True)

	def generate(self, annotation_image_dir, annotation_file_name, landmark_image_dir, landmark_file_name, base_number_of_images, target_root_dir):

		if(not os.path.isfile(annotation_file_name)):
			return(False)
		if(not os.path.exists(annotation_image_dir)):
			return(False)

		if(not os.path.isfile(landmark_file_name)):
			return(False)
		if(not os.path.exists(landmark_image_dir)):
			return(False)

		target_root_dir = os.path.expanduser(target_root_dir)
		target_root_dir = os.path.join(target_root_dir, self.network_name())
		if(not os.path.exists(target_root_dir)):
			os.makedirs(target_root_dir)

		minimum_face = NetworkFactory.network_size(self.network_name())

		print('Generating landmark samples.')
		if(not self._generate_landmark_samples(landmark_image_dir, landmark_file_name, minimum_face, target_root_dir)):
			print('Error generating landmark samples.')
			return(False)
		print('Generated landmark samples.')

		print('Generating image samples.')
		if(not self._generate_image_samples(annotation_image_dir, annotation_file_name, minimum_face, target_root_dir)):
			print('Error generating image samples.')
			return(False)
		print('Generated image samples.')

		if(not self._generate_image_list(base_number_of_images, target_root_dir)):
			return(False)

		print('Generating TensorFlow dataset.')
		if(not self._generate_dataset(target_root_dir)):
			print('Error generating TensorFlow dataset.')
			return(False)
		print('Generated TensorFlow dataset.')

		return(True)


