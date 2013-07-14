import twitter
import urllib
import AccountConstants as CO

twitter_consumer_key = CO.twitter_consumer_key
twitter_consumer_secret = CO.twitter_consumer_secret
twitter_access_token_key = CO.twitter_access_token_key
twitter_access_token_secret = CO.twitter_access_token_secret

class ShortenURL(object):
    '''Helper class to make URL Shortener calls if/when required'''
    def __init__(self,userid=None,password=None):
        '''Instantiate a new ShortenURL object
        
        Args:
            userid:   userid for any required authorization call [optional]
            password: password for any required authorization call [optional]
        '''
        self.userid   = userid
        self.password = password

    def Shorten(self,
               longURL):
        '''Call TinyURL API and returned shortened URL result
        
        Args:
            longURL: URL string to shorten
        
        Returns:
            The shortened URL as a string

        Note:
            longURL is required and no checks are made to ensure completeness
        '''

        result = None
        f      = urllib.urlopen("http://tinyurl.com/api-create.php?url=%s" % longURL)
        try:
            result = f.read()
        finally:
            f.close()

        return result

def pushToTwitter(msg):
    api = twitter.Api(consumer_key=twitter_consumer_key,consumer_secret=twitter_consumer_secret,access_token_key=twitter_access_token_key,access_token_secret=twitter_access_token_secret)
    try:
        api.PostUpdate(msg)
    except Exception as e:
        print "!!:pushToTwitter Exception:%s" % e 
    return
