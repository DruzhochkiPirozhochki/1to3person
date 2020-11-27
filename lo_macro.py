# coding: utf-8
from __future__ import unicode_literals
import urllib, json
import urllib.request


def my_first_macro():
    doc = XSCRIPTCONTEXT.getDocument()
    text = doc.getText()

    tRange = text.End
    tRange.String = "KEKEKEK"

    toSend = {'fname': "Artem Dmitriev", "text": tRange.String}
    data = json.dumps(toSend).encode("utf8")
    url = 'http://localhost:8080/send'
    req = urllib.request.Request(url, data=data, headers={'content-type': 'application/json'})

    res = urllib.request.urlopen(req)

    res_body = res.read()

    # https://docs.python.org/3/library/json.html
    j = json.loads(res_body.decode("utf-8"))
    tRange.String = j['text']

    return
