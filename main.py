#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Gilles de Hollander on 2012-08-04.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import random
from music21 import *
import math
import time
import pickle

from musical_ngrams import *



def main():
	pass


if __name__ == '__main__':		
	
	# paths = corpus.getComposer('essenFolksong')
	# 
	#  score = corpus.parse(paths[0])
	#	 
	sng = ScoreNGrammer()
	
	# paths = corpus.getComposer('bach')
	# paths = corpus.getComposer('essenFolksong')
	# sBach = corpus.parse('bach/bwv7.7')
	
	# sBach = corpus.parse(paths[0])
	
	# ng = nGram()
	
    # ng = pickle.load(open('ng10_mozart-v2.pkl'))
	ng = pickle.load(open('ng5_bach-v2.pkl'))
    # ng = pickle.load(open('ng10_mozart-v1.pkl'))
	
	# for path in paths[0:3]:
	#   print 'Adding n-grams in %s' % path
	#   current_s = corpus.parse(path)
	#   
	#   n_scores = len(current_s.scores)
	#   
	#   for i, score in enumerate(current_s.scores):
	#	 if i % int(n_scores /10) == 0:
	#		 print 'Adding score %d/%d' % (i+1, n_scores)
	#	 n_parts = len(score.parts)
	#	 for j, part in enumerate(score.parts):
	#		 ng.join_ngram(sng.process_score(part.flat.notesAndRests))
	# 
	# print 'Done adding'
	rg = randomMusicGenerator(ng, weighted_choice=True)
	seq = rg.create_sequence(32)
	
    # seq = evo.stream
	
	# sp = midi.realtime.StreamPlayer(seq)
	# sp.play()
	
	evo = Evolution(ng, seq, mutation_n=2500)
	
		 # print evo.fitness_scorer.give_fitness(seq)
		 # print evo.fitness_scorer.give_fitness(seq2)
	
	while(True):
		# sp = midi.realtime.StreamPlayer(evo.evolve())
		# sp.play()
		evo.evolve()
	  # time.sleep(2)
	
	
	# sp = midi.realtime.StreamPlayer(seq2)
	# sp.play()
	