#!/usr/bin/env python
# encoding: utf-8
"""
create_ngrams.py

Created by Gilles de Hollander on 2012-08-05.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from musical_ngrams import *


def main():
	pass


if __name__ == '__main__':
	main()

	sng = ScoreNGrammer()
	
	paths = corpus.getComposer('bach')
	#paths = corpus.getComposer('essenFolksong')
	# paths = corpus.getComposer('mozart')
	# sBach = corpus.parse('bach/bwv7.7')
	
	# sBach = corpus.parse(paths[0])
	
	ng = nGram()
	# 
	for (i_path, path) in enumerate(paths):
		print 'Adding n-grams in %s (%d/%d)' % (path, i_path+1, len(paths))
		current_s = corpus.parse(path)
		

		
		if type(current_s) == stream.Score:
			for j, part in enumerate(current_s.parts):
				ng.join_ngram(sng.process_score(part.flat.notesAndRests))
		
		else:
			n_scores = len(current_s.scores)
			for i, score in enumerate(current_s.scores):
				if i % int(n_scores /5) == 0:
					print 'Adding score %d/%d' % (i+1, n_scores)
				n_parts = len(score.parts)
				for j, part in enumerate(score.parts):
					ng.join_ngram(sng.process_score(part.flat.notesAndRests))