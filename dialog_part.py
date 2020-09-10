
class dialogSystem():
	def __init__(self):
		self.sentences = []
		self.add_sentences()

	def reply(self,res_id):
		return self.sentences[res_id]

	def add_sentences(self):
		self.sentences.append("I want to know your preference. I will show you 30 popular movies and please tell me whether you like it if you have watched the movie.")
		self.sentences.append("Thanks for your opinions. And I will recommend you 4 movies.")
		self.sentences.append("I will recommend you: ")
		self.sentences.append(".\nBecause it has the following features: \n")
		self.sentences.append("Do you think you will watch it?")
		self.sentences.append("Which reason makes you feel you won't watch it?")
		self.sentences.append("Do you think you will watch the movie: ")
		self.sentences.append("? \nYou can keep your idea before.")
		self.sentences.append("you have watched #these movies include the feature #So I think you actually like the feature.")
		self.sentences.append("Thank you! The task is over!")