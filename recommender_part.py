import csv
import json
import numpy as np

class recommenderSystem():
	def __init__(self):
		self.dataset = open('./dataset/tmdb.csv','r')
		self.origin_data = []
		self.read_data()

	def read_data(self):
		reader = csv.reader(self.dataset)
		header = next(reader)
		self.origin_data = [row for row in reader]
		self.scores = []

	def extract_favo_feats(self, um):
		all_feats = []
		all_feats_dict = {}
		for i in um.pref_movies_id:
			for f in eval(self.origin_data[i][4]):
				all_feats.append(f['name'])
		for f in all_feats:
			if f not in all_feats_dict:
				all_feats_dict[f] = 1
			else:
				all_feats_dict[f] += 1

		um.favo_feats = {f:all_feats_dict[f] for f in all_feats_dict if all_feats_dict[f] >= 2}

	def make_recommendation(self, um):
		curr_score = 0
		for row in self.origin_data:
			curr_score = 0
			for f in eval(row[4]):
				if f['name'] in um.favo_feats:
					curr_score += um.favo_feats[f['name']]
			self.scores.append(curr_score)
		recommend_list_id = list(reversed(np.argsort(self.scores)))
		recommended = []
		for i in recommend_list_id:
			if len(recommended) >=4:
				break
			if i not in um.not_recommended:
				um.not_recommended.append(i)
				recommended.append(i)
		um.recommended = recommended

if __name__ == '__main__':
	a=recommenderSystem()