import sys
import os
import random
from music21 import *
import math



STANDARD_SF = 0.05
STANDARD_N = 10
N = 5

class nGram:
    
    def __init__(self, smooth_factor=None, smooth_n=None, n=N):
        
        self.counts = {}        
        self.total_counter = {}
        self.n = n
        
        if smooth_factor == None:
            self.sf = dict([(i, STANDARD_SF*i) for i in range(1,self.n+1)])
        else:
            self.sf = smooth_factor
            
        if smooth_n == None:
            self.sn = dict([(i, STANDARD_N**i) for i in range(1,self.n+1)])
        else:
            self.sn = smooth_n
        
    
    
    def add_example(self, example, prop=None):
        
        
        if prop not in self.counts:
            self.counts[prop] = dict([(i,{}) for i in range(1,self.n+1)])
            self.total_counter[prop] = dict([(i,0) for i in range(1,self.n+1)])
        
        for n in range(1, self.n+1):
            for (i, start) in enumerate(range(len(example)-n+1)):
                
                
                current_ngram = tuple(example[i:i+n])
                
                if current_ngram not in self.counts[prop][n]:
                    self.counts[prop][n][current_ngram] = 1                
                else:
                    self.counts[prop][n][current_ngram] += 1
            
                self.total_counter[prop][n] += 1
        
    
    def get_probability(self, example, prop=None):
        
        n = len(example)
        
        
        if n > self.n:
            raise Error('Example is too long. only n < %d' % self.n)
        
        
        # print 'probability of %s (%s)' % (example, prop)
        if example in self.counts[prop][n]:
            # print self.counts[prop][n][example] / float(self.total_counter[prop][n]) * (1-self.sf[n])
            return self.counts[prop][n][example] / float(self.total_counter[prop][n]) * (1-self.sf[n])
            
        else:
            # print self.sf[n] / self.sn[n]
            return self.sf[n] / self.sn[n]
            
    def join_ngram(self, other_ngram):
        
        
        for n in range(1, N+1):
            for prop in other_ngram.counts.keys():
                
                if prop not in self.counts.keys():
                    self.counts[prop] = {}
                    self.total_counter[prop] = {}
                
                if n not in self.counts[prop].keys():
                    self.counts[prop][n] = {}
                    self.total_counter[prop][n] = 0
                
                for sequence in other_ngram.counts[prop][n]:
                    
                    if sequence in self.counts[prop][n]:
                        self.counts[prop][n][sequence] += other_ngram.counts[prop][n][sequence]
                    else:
                        self.counts[prop][n][sequence] = other_ngram.counts[prop][n][sequence]
                
                self.total_counter[prop][n] += other_ngram.total_counter[prop][n]
                    

class BayesianModel():
    
    def __init__(self):
        pass

class ScoreNGrammer():
    
    def __init__(self):
        self.properties = {}
        
    def regularize_score(self, score):
        
        
        
        distanceToC = 0
        
        for current_note in score.notes:
            
            if not current_note.isRest and not current_note.isChord:        
                referenceC = note.Note("C4") 
                distanceToC = interval.notesToInterval(current_note, referenceC) 
                
        
        score = score.transpose(distanceToC)
        
        return score
        
    
    def process_score(self, score):
        score = self.regularize_score(score)
        ng = nGram()
        
        notes = [str(note.pitch) if not note.isRest and not note.isChord else None for note in score]
        intervals = notesToIntervals(score)
        durations = [float(note.duration.quarterLength) for note in score]
        
        ng.add_example(notes, prop='notes')
        ng.add_example(intervals, prop='intervals')
        ng.add_example(durations, prop='durations')
        ng.add_example(zip(intervals, durations), prop='interval_durations')
                
        return ng
        
        
        

def notesToIntervals(notes):
    
    result = [None]
    
    for i in range(1, len(notes)):
    
        
        if notes[i].isChord or notes[i-1].isChord:
            result.append('chord')
        
        elif not notes[i-1].isRest and not notes[i].isRest:
            result.append(interval.notesToChromatic(notes[i-1], notes[i]).semitones)
            
        elif notes[i].isRest and not notes[i-1].isRest:
            result.append('toRest')
        
        elif not notes[i].isRest and notes[i-1].isRest:
            result.append('fromRest')
        
        elif notes[i].isRest and notes[i-1].isRest:
            result.append('restToRest')
            
            
            
    return result

class randomMusicGenerator(object):
    
    def __init__(self, ngram, weighted_choice=False):
        self.ngram = ngram
        self.weighted_choice = weighted_choice
        
    def create_sequence(self, duration):
        
        current_duration = 0
        
        possible_durations = self.ngram.counts['durations'][1].keys()
        
        
        # possible_durations = [(0.25,), (0.5,), (1.0,), (1.5,), (2.0,), (3.0,), (4.0,)]
        
        possible_intervals = self.ngram.counts['intervals'][1].keys()
        possible_notes = self.ngram.counts['notes'][1].keys()
        
        notes = []
        durations = []
        candidates = []
        
        while(current_duration < duration):
            for cand_note in possible_notes:
                for cand_duration in possible_durations:

                    # print 'Trying out note %s and duration %s' % (cand_note, cand_duration)
                    
                    prob = self.ngram.get_probability(cand_note, 'notes') * self.ngram.get_probability(cand_duration, 'durations')
                    
                    # print notes
                    # print durations
                    for i in range(1, min(N, len(durations)+1)):
                        prob *= self.ngram.get_probability(tuple(notes[-i:]) + cand_note, 'intervals')
                        prob *= self.ngram.get_probability(tuple(durations[-i:]) + cand_duration, 'durations')
                    
                    candidates.append(((cand_note, cand_duration), prob))
                    
            # print candidates
            if self.weighted_choice:
                choice = weighted_choice(candidates)
            else:
                choice = random.choice([cand[0] for cand in candidates])
            
            notes.append(choice[0][0])
            durations.append(choice[1][0])
            
            current_duration += float(choice[1][0])
            
        return self.sequence_to_stream(notes, durations)
        
    def sequence_to_stream(self, notes, durations):
        
        output_stream = stream.Stream()

        
        for i in range(len(durations)):
            n = note.Note(notes[i])
            n.duration.quarterLength = float(durations[i])
            print n.name
            output_stream.append(n)
        
        return output_stream
        


class Evolution(object):
    
    def __init__(self, ngram, s, limit_durations=False, mutation_prob=0.1, mutation_n=1000):
        self.ng = ngram
        self.stream = s
        self.mutation_prob = mutation_prob
        self.mutation_n = mutation_n
        
        self.possible_durations = [float(d[0]) for d in self.ng.counts['durations'][1].keys()]
        self.possible_notes = [n[0] for n in self.ng.counts['notes'][1].keys()]
        
        if limit_durations:
            self.possible_durations = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
        
        self.fitness_scorer = StreamFitnessScorer(self.ng)
        
        
    def create_new_generation(self):
        
        gen = []
        
        for i in range(self.mutation_n):
            # if i % int(self.mutation_n/20) == 0:
            #     print '%d/%d' % (i, self.mutation_n)
            new_child = self.mutate(self.stream)
            gen.append((new_child, self.fitness_scorer.give_fitness(new_child)))
            
        return gen
    
    def evolve(self):
        gen = self.create_new_generation()
        scores = [g[1] for g in gen]
        
        best_child = gen[scores.index(max(scores))][0]
        self.stream = best_child
        
        best_child.show('text')
        print 'Best score now: %f' % max(scores)
        
        return best_child
    
    
    def mutate(self, current_stream):
        
        new_stream = stream.Stream()
        
        for i in range(len(current_stream)):
            
            
            n = current_stream[i]
            
            # Mutate pitch?
            if random.random() < self.mutation_prob:
                n = note.Note(random.choice(self.possible_notes))
                n.duration.quarterLength = current_stream[i].duration.quarterLength
                        
            # Mutate duration?
            if random.random() < self.mutation_prob:
                n.duration.quarterLength = random.choice(self.possible_durations)
            
            new_stream.append(n)
                
        
        return new_stream
        

class StreamFitnessScorer():
    
    def __init__(self, ngram):
        self.ngram = ngram
        self.cache = {}
        
    
    def give_fitness(self, target_stream):
        
        notes, durations = self.get_notes_durations_from_stream(target_stream)
        
        notes = tuple(notes)
        durations = tuple(durations)
        
        intervals = notesToIntervals(target_stream)
        
        intervals = tuple(intervals)
        fitness = 0
        
        # A PRIORI model
        for i in range (len(notes)):
            fitness += math.log(self.ngram.get_probability((notes[i],), 'notes'))
            
        
        for n in range(1, N):
            for i in range(len(notes) + 1 - N):
            
                fitness += math.log(self.ngram.get_probability(durations[i:i+n], 'durations'))
                fitness += math.log(self.ngram.get_probability(intervals[i:i+n], 'intervals'))
                fitness += math.log(self.ngram.get_probability(tuple(zip(intervals[i:i+n], durations[i:i+n])), 'interval_durations'))
                
                # if (durations[i:i+n], intervals[i:i+n]) not in self.cache.keys():
                #     current_fitness = 0
                #     current_fitness += math.log(self.ngram.get_probability(durations[i:i+n], 'durations'))
                #     current_fitness += math.log(self.ngram.get_probability(intervals[i:i+n], 'intervals'))
                #     current_fitness += math.log(self.ngram.get_probability(tuple(zip(intervals[i:i+n], durations[i:i+n])), 'interval_durations'))
                #     self.cache[(durations[i:i+n], intervals[i:i+n])] = current_fitness
                # 
                #     fitness += current_fitness
                # else:
                #     fitness += self.cache[(durations[i:i+n], intervals[i:i+n])]
                
        
        return fitness
            
            
    def get_notes_durations_from_stream(self, target_stream):
        
        notes = []
        durations = []
        
        for i in range(len(target_stream)):
            if not target_stream[i].isRest:
                notes.append(str(target_stream[i].pitch))
            else:
                notes.append(None)
            
            durations.append(target_stream[i].duration.quarterLength)
            
        return notes, durations
        
        

def weighted_choice(choices):
   total = sum(w for c,w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto+w > r:
         return c
      upto += w
   assert False, "Shouldn't get here"