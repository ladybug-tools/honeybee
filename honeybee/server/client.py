import urllib
import urllib2
import json
from mpupload import MultiPartForm


class Client():
    """Client class for honeybee to set requests to server."""

    def __init__(self, url):
        self.url = url
        self.headers = {
            'Content-Type': 'application/zip'
        }

    def uploadFile(self, filename):
        """Upload a file and send it to the server."""
        form = MultiPartForm()
        # add file
        form.addFile('file', filename, open(filename, 'rb'))
        request = urllib2.Request(self.url)
        body = str(form)
        request.add_header('Content-type', form.getContentType())
        request.add_header('Content-length', len(body))
        request.add_data(body)
        request.get_data()
        data = urllib2.urlopen(request).read()
        return data
