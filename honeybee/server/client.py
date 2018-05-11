import urllib2
from mpupload import MultiPartForm


class Client():
    """Client class for honeybee to set requests to server."""

    def __init__(self, url):
        self.url = url
        self.headers = {
            'Content-Type': 'application/zip'
        }

    def upload_file(self, filename):
        """Upload a file and send it to the server."""
        form = MultiPartForm()
        # add file
        form.add_file('file', filename, open(filename, 'rb'))
        request = urllib2.Request(self.url)
        body = str(form)
        request.add_header('Content-type', form.get_content_type())
        request.add_header('Content-length', str(len(body)))
        request.add_data(body)
        request.get_data()
        data = urllib2.urlopen(request).read()
        return data
