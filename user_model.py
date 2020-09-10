import csv
from recommender_part import recommenderSystem
class userModel():
	def __init__(self):
		self.user_id = ''
		self.channel_id = ''
		self.pref_movies_id = []
		self.favo_feats = {}
		self.not_recommended = [68, 19, 3232, 329, 55, 2912, 1337, 102, 3719, 77, 87, 1465, 276, 7, 17, 1881, 506, 262, 809, 335, 1, 64, 456, 362, 693, 238, 3337, 16, 2522, 12, 662, 0, 9, 124, 96, 270, 65, 3865, 26, 108, 88, 200, 82, 199, 28, 127, 94, 788, 95, 546]
		self.recommended = []


if __name__ == '__main__':
	rs = recommenderSystem()
	um = userModel()
	rs.extract_favo_feats(um)
	rs.make_recommendation(um)