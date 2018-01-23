import random
import requests
import json

def shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyBNgFqIbtYuj9ebMqS9gnZOvkhmx78mQkY'
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    short_url = json.loads(r.text)
    return short_url['id']

def getSimpsonsQuote(questions):
	frinkiacUrl = requests.get('https://frinkiac.com/api/random')
	if frinkiacUrl.status_code == 200:
		frinkiacJson = frinkiacUrl.json()

		episode = frinkiacJson['Frame']['Episode']
		timestamp = frinkiacJson['Frame']['Timestamp']
		if episode == 'Movie':
			season = 13
		else:
			season = int(episode[episode.find('S')+1:episode.find('E')])
		frinkiacUrl = 'https://frinkiac.com/caption/' + str(episode) + '/' + str(timestamp)
		imageUrl = 'https://frinkiac.com/img/' + str(episode) + '/' + str(timestamp) + '.jpg'
		shortUrl = shorten_url(imageUrl)
		caption = '\n'.join([subtitle['Content'] for subtitle in frinkiacJson['Subtitles']])
		if season <= 12:
			return questions + caption.replace('\n',' ') + ' ' + shortUrl + '`' + frinkiacJson['Episode']['Title'] + '\n'
		else:
			return questions

	else:
		return questions

def getQuotes(count):
	message = ''
	for i in range(count):
		if i%5==0:
			print(i)
		message = getSimpsonsQuote(message)
	return message
