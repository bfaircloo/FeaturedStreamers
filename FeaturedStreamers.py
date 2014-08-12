import urllib, json, sys, os
from PIL import Image
from PIL import ImageColor

f=open('FeaturedStreamers.txt')
streamers = [i for i in f.readlines()]
f.close

games = []
names = []
cwd = os.getcwd()

# Create Directories
if not os.path.exists(cwd + '\\Output'):
        os.makedirs(cwd + '\\Output')

if not os.path.exists(cwd + '\\Output\\FeaturedStreamers'):
        os.makedirs(cwd + '\\Output\\FeaturedStreamers')

# Downloads avatar and game images for each streamer
for x in range(0, len(streamers)):
	streamers[x]=streamers[x].lower().strip()

	# request streamer information from Twitch API
	print('\nDownloading ' + str(streamers[x]) + '\'s avatar...')
	response = urllib.urlopen('https://api.twitch.tv/kraken/channels/' + streamers[x])
	j_obj = json.load(response)

	# get streamer display name
	names.append(j_obj['display_name'].encode('utf-8'))

	# get streamer avatar url
	avatar_url = j_obj['logo']
	if (avatar_url != None):
		avatar_url.encode('utf-8')
	else:
		avatar_url = 'http://static-cdn.jtvnw.net/jtv_user_pictures/twitch-profile_image-94a42b3a13c31c02-300x300.jpeg'.encode('utf-8')
	
	# get the name of the game that the streamer last played
	games.append(j_obj['game'])
	if(games[x] != None):
		games[x] = games[x].encode('utf-8')

	# download streamer's avatar to the Output\FeaturedStreamers\ directory
	urllib.urlretrieve(avatar_url, 'Output\FeaturedStreamers\streamer' + str(x) + '.png')

	# Tries to download game image from Twitch with fallbacks to GiantBomb and then default Twitch game image 
	if (games[x] != None):
		# request game information from Twitch API
		print('Making request to Twitch API...')
		twitch_response = urllib.urlopen('https://api.twitch.tv/kraken/search/games?q=' + str(games[x]) + '&type=suggest&live=false')
		j_twitch = json.load(twitch_response)
		gb_id = None
		twitch_game_img = None

		# results of the game name query
		game_search_results = j_twitch['games']

		# grab the id and image from the game with the same name that is stored in games[]
		print ('Grabbing GiantBomb game ID and Twitch game image url...')
		if len(game_search_results) > 1:
			for m in range(0, len(game_search_results)):
				if j_twitch['games'][m]['name'].encode('utf-8') == games[x]:
					gb_id = j_twitch['games'][m]['giantbomb_id']
					twitch_game_img = j_twitch['games'][m]['box']['large']
		else:
			gb_id = j_twitch['games'][0]['giantbomb_id']
			twitch_game_img = j_twitch['games'][0]['box']['large']

		# download game's image to the Output\FeaturedStreamers\ directory
		print('Downloading ' + str(games[x]) + ' image...')
		urllib.urlretrieve(twitch_game_img, 'Output\FeaturedStreamers\game' + str(x) + '.png')

		# Downloads game image from GiantBomb, if Twitch returned default game image
		img = Image.open('Output\\FeaturedStreamers\\game' + str(x) + '.png')
		if img.getpixel((0,0)) == (103, 68, 168) and gb_id != None:
			# request game information from GiantBomb API
			print('Making request to GiantBomb API...')
			gb_response = urllib.urlopen('http://www.giantbomb.com/api/game/3030-' + str(gb_id) + '/?api_key=99e5633b5e5a3b91480fdb848c8387b1e7cfac54&format=json')
			j_gb = json.load(gb_response)

			# downloads game image
			gb_game_img = j_gb['results']['image']['small_url']
			print('Downloading ' + str(games[x]) + ' image from GiantBomb...')
			urllib.urlretrieve(gb_game_img, 'Output\FeaturedStreamers\game' + str(x) + '.png')

			# adjusts image to display nicely at a resolution of 272x380 px
			print('Resizing game image...')
			background_img = Image.new('RGB', (272,380), ImageColor.getrgb('rgb(103,68,168)'))
			#background_img.putalpha(0)
			im = Image.open('Output\\FeaturedStreamers\\game' + str(x) + '.png')
			im.thumbnail((272, 380), Image.ANTIALIAS)
			background_img.paste(im,(((272-im.size[0])/2),((380-im.size[1])/2)))
			background_img.save('Output\\FeaturedStreamers\\game' + str(x) + '.png')

	else:
		print('Downloading default game image from Twitch...\n')
		urllib.urlretrieve('http://static-cdn.jtvnw.net/ttv-static/404_boxart-272x380.jpg', "Output\FeaturedStreamers\game" + str(x) + ".png")

	# Write streamers names to separate text files
	f=open('Output\\FeaturedStreamers\\Streamer' + str(x) + 'Name.txt', 'w')
	f.write(names[x])
	f.close