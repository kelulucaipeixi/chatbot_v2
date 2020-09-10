from slack import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask,request
import os
import json
import time
from copy import deepcopy
from dialog_part import dialogSystem
from recommender_part import recommenderSystem
from user_model import userModel

app = Flask(__name__)
um = userModel()
rs = recommenderSystem()
ds = dialogSystem()

chatbot_id = 'U01556TH79A'
# chatbot_id = 'U0188FRH2J1'

json_file1 = open('json/preference_extractor.json','r')
json_file2 = open('json/recommendation_maker.json','r')
json_file3 = open('json/reason_extractor.json','r')
json_file4 = open('json/recommendation_confirmer.json','r')
preference_extractor = json.load(json_file1)
recommendation_maker = json.load(json_file2)
reason_extractor = json.load(json_file3)
recommendation_confirmer = json.load(json_file4)
preference_extractor_pointer = 0
recommendation_maker_pointer = 0
reason_extractor_pointer = 0

json_file4 = open('data_preprocessing/pop50_id.json','r')
json_file5 = open('data_preprocessing/pop50_name.json','r')
pop50_id = json.load(json_file4)
pop50_name = json.load(json_file5)

slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events",app)

def get_res_id(text):
	pass

def make_responses(res_id):
	if res_id == 1:
		get_preference()
	else:
		return ds.reply(res_id)

# system will send some sentences default.
def send_sentences(sentence):
	slack_web_client.chat_postMessage(
			channel = um.channel_id,
			text = sentence)

def init_preference_extractor():
	preference_extractor[0]['text'] = pop50_name[preference_extractor_pointer]

# send blocks of movie information to acquire user preference
def get_preference():
	init_preference_extractor()
	slack_web_client.chat_postMessage(
            channel = um.channel_id,
            attachments = preference_extractor)

def init_recommendation_maker():
	recommendation_maker[0]['text'] = ds.sentences[2] + \
	rs.origin_data[um.recommended[recommendation_maker_pointer]][6] + ds.sentences[3]
	for f in eval(rs.origin_data[um.recommended[recommendation_maker_pointer]][4]):
		if f['name'] in um.favo_feats:
			recommendation_maker[0]['text'] = recommendation_maker[0]['text'] + f['name'] +', '
	recommendation_maker[0]['text'] = recommendation_maker[0]['text'][:-2] + '.\n' + ds.sentences[4]

# send blocks of recommendation to user
def send_recommendation():
	init_recommendation_maker()
	slack_web_client.chat_postMessage(
            channel = um.channel_id,
            attachments = recommendation_maker)

def init_get_reason():
	reason_extractor_changed = deepcopy(reason_extractor)
	reason_extractor_changed[0]['text'] = ds.sentences[5]
	for f in eval(rs.origin_data[um.recommended[recommendation_maker_pointer]][4]):
		if f['name'] in um.favo_feats:
			curr_dict = {'text': f['name'], 'value': f['name']}
			reason_extractor_changed[0]['actions'][0]['options'].insert(0,curr_dict)
	return reason_extractor_changed

def get_reason():
	reason_extractor_changed = init_get_reason()
	slack_web_client.chat_postMessage(
            channel = um.channel_id,
            attachments = reason_extractor_changed)

def send_explanations(feat):
	origin_sentence = ds.sentences[8]
	feat_in_movies = []
	for i in um.pref_movies_id:
		for f in eval(rs.origin_data[i][4]):
			if f['name'] == feat:
				feat_in_movies.append(rs.origin_data[i][6])
	index_1 = ds.sentences[8].find('#')		
	ds.sentences[8] = ds.sentences[8].replace('#','',1)
	index_2 = ds.sentences[8].find('#')
	ds.sentences[8] = ds.sentences[8].replace('#','',1)
	sentence_list = list(ds.sentences[8])
	sentence_list.insert(index_2,feat+', ')
	for i in feat_in_movies:
		sentence_list.insert(index_1,i+', ')
	ds.sentences[8] = ''.join(sentence_list)
	send_sentences(ds.sentences[8])
	ds.sentences[8] = origin_sentence

def init_resend_recommendation():
	recommendation_confirmer[0]['text'] = ds.sentences[6] + \
	rs.origin_data[um.recommended[recommendation_maker_pointer]][6] + ds.sentences[7]

def resend_recommendation():
	init_resend_recommendation()
	slack_web_client.chat_postMessage(
            channel = um.channel_id,
            attachments = recommendation_confirmer)

@slack_events_adapter.on("message")
def handle_message(event_data):
	global user_id
	global first_sentence
	message = event_data["event"]
	text = message.get('text')
	if um.user_id == '':
		um.user_id = message.get('user')
		um.channel_id = message.get('channel')
	if text in ds.sentences:
		pass
	elif message.get("subtype") is None and message['user'] == um.user_id:
		send_sentences(ds.sentences[0])
		get_preference()
	

@app.route("/slack/message_actions",methods=['POST'])
def message_actions():
	global preference_extractor_pointer
	global recommendation_maker_pointer
	global pop50_id
	global pop50_name
	form_json = json.loads(request.form['payload'])
	if 'callback_id' in form_json and form_json['callback_id'] == 'preference_extractor':
		value = form_json['actions'][0]['value']
		ans = pop50_name[preference_extractor_pointer] + ": " + form_json['original_message']['attachments'][0]['actions'][int(value)]['text']
		if form_json['original_message']['attachments'][0]['actions'][int(value)]['value'] == '1':
			um.pref_movies_id += [pop50_id[preference_extractor_pointer]]
		if preference_extractor_pointer < 9:
			if preference_extractor_pointer % 10 == 8:
				send_sentences("Please wait for 60 seconds.")
				time.sleep(60)
			preference_extractor_pointer += 1
			get_preference()
		else:
			rs.extract_favo_feats(um)
			text = ds.sentences[1]
			send_sentences(text)
			rs.make_recommendation(um)
			send_recommendation()
		return ans
	elif 'callback_id' in form_json and form_json['callback_id'] == 'recommendation_maker':
		value = form_json['actions'][0]['selected_options'][0]['value']
		value_int = int(value[0])
		ans = rs.origin_data[um.recommended[recommendation_maker_pointer]][6] + ':  ' + value
		if value_int <= 3:
			get_reason()
		elif recommendation_maker_pointer < 3:
			recommendation_maker_pointer += 1
			send_recommendation()
		else:
			send_sentences(ds.sentences[-1])
		return ans
	elif 'callback_id' in form_json and form_json['callback_id'] == 'reason_extractor':
		value = form_json['actions'][0]['selected_options'][0]['value']
		ans = value
		if value == "None of the above are the reasons I don't like the movie.":
			if recommendation_maker_pointer < 3:
				recommendation_maker_pointer += 1
				send_recommendation()
			else:
				send_sentences(ds.sentences[-1])
			return ans
		else:
			send_explanations(value)
			resend_recommendation()
			return ans
	elif 'callback_id' in form_json and form_json['callback_id'] == 'recommendation_confirmer':
		value = form_json['actions'][0]['selected_options'][0]['value']
		ans = rs.origin_data[um.recommended[recommendation_maker_pointer]][6] + ':  ' + value
		if recommendation_maker_pointer < 3:
			recommendation_maker_pointer += 1
			send_recommendation()
		else:
			send_sentences(ds.sentences[-1])
		return ans
	else:
		print(form_json['callback_id'])
		return "error"

if __name__ == '__main__':
	app.run(port = 3000)