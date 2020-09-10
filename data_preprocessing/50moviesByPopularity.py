import csv
import json

f = open('../dataset/tmdb.csv','r')
reader = csv.reader(f)
header = next(reader)
data = [(row[8],row[6]) for row in reader]
popularity = [t[0] for t in data]
names = [t[1] for t in data]
paired_popularity = [(i,float(popularity[i])) for i in range(len(popularity))]
sorted_num = sorted(paired_popularity, key = lambda t: t[1])

pop50_id = [t[0] for t in sorted_num[-50:]]
pop50_name = [names[i] for i in pop50_id]
out_id = open('pop50_id.json','w')
json.dump(pop50_id, out_id)
out_name = open('pop50_name.json','w')
json.dump(pop50_name, out_name)
