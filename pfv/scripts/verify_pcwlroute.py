from pymongo import *
client = MongoClient()
db = client.nm4bd

def is_shortest_route(dlist,ideal_distance):
	total_d = 0
	distance = 0
	first_flag = True
	first_d = 0
	for route_list in dlist:
		total_d = 0
		for i in range(0,len(route_list)):
			distance = route_list[i]["distance"]
			total_d += distance
		
		if first_flag:
			first_d = total_d
			if first_d != ideal_distance:
				print("distance error")
				return False
			first_flag = False
		elif total_d < first_d:
			print(dlist)
			return False
	return True

def verify_pcwlroute():
	pcwlroute = []
	ideal_one_route = []
	count = 0
	distance = 0

	pcwlroute += db.pcwlroute_test.find()
	for one_route in pcwlroute:
		ideal_one_route = []
		ideal_one_route += db.idealroute.find({"$and": [
                                                    {"floor" : one_route["floor"]},
                                                    {"query" : one_route["query"][0]}, 
                                                    {"query" : one_route["query"][1]}
                                              ]})
		if len(ideal_one_route) != 1:
			print("error")
		else:
			is_shortest = is_shortest_route(one_route["dlist"],ideal_one_route[0]["total_distance"])
			if is_shortest:
				count += 1
	print(str(count)+" out of "+str(len(pcwlroute)))


if __name__ == '__main__':
	verify_pcwlroute()