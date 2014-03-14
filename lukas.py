import json
import urllib2

def get_person_info(username):
    request_url = "http://lukas.dev.yelp.com:7777/yelployees?yelp_id="
    req = urllib2.urlopen(request_url + username)
    resp = json.loads(req.read())[0]
    if len(resp['photo_urls']) == 0:
        resp['photo_url'] = 'http://wwcfdc.com/new/wp-content/uploads/2012/07/facebook-no-image11.gif'
    else:
        resp['photo_url'] = resp['photo_urls'][0]
    del resp['photo_urls']
    return resp
