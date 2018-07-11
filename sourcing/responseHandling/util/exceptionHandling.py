import requests
import logging

def tryForHtml(url,tries=0,limit=6):

    if tries < limit:
        try:
            r = requests.get(url)

        except requests.exceptions.ConnectionError:
            delay = 1 + (1*tries)
            logging.warning('connection error for %s!'%(url))
            logging.warning('sleeping for ... %i'%(delay))
            time.sleep(delay)
            tries += 1
            html = tryForHtml(url,tries=tries)

        except requests.exceptions.HTTPError:
            logging.warning('http-error for %s!'%(url))
            html = ''

        except requests.exceptions.Timeout:
            logging.warning('%s timed out!'%(url))
            html = ''

        except:
            logging.warning('some other exception...')
            html = ''

        else:
            html = r.text

    else:
        html = ''

    return(html)
