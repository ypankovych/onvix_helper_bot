import requests
from lxml import etree

favorite_url = 'https://onvix.tv/playlists/favorites/toggle.json'
favorites = 'https://onvix.tv/playlists/short_info.json'
sign_in = 'https://onvix.tv/users/sign_in'


def login(email, password, flag='true'):
	with requests.Session() as user_session:
		response = user_session.post(sign_in, data={
            'user[email]': email,
            'user[password]': password,
            'user[remember_me]': flag
        })
		if check_auth(user_session):
			html_object = etree.HTML(response.text)
			token = html_object.xpath('/html/head/meta[10]')[0].get('content')
			return {'session': user_session, 'token': token}
		return False


def check_auth(user):
	if user.get(favorites).json().get('error'):
		return False
	return True


def get_favorites(user):
	data = user.get(favorites).json()
	return data['favorites']['material_ids']


def set_favorite(user, token, id):
	user.post(favorite_url, files={'': ''},
		data={'id': 'favorites', 
			'material_id': id, 
			'authenticity_token': token})


def process(user, materials):
	for material_id in materials:
		set_favorite(user['session'], user['token'], material_id)
