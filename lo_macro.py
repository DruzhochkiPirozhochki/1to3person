# # coding: utf-8
from __future__ import unicode_literals
import urllib, json
import urllib.request
import re
from com.sun.star.drawing.TextHorizontalAdjust import LEFT


def OneToThree(args=''):
    # preparation
    desktop = XSCRIPTCONTEXT.getDesktop()
    model = desktop.getCurrentComponent()
    oSelected = model.getCurrentSelection()
    doc = XSCRIPTCONTEXT.getDocument()
    startText = doc.getText()

    # acquiring the selected text
    oSel = oSelected.getByIndex(0)
    selectedText = oSel.getString()

    # obtaining all text
    allText = startText.Text.String

    # splitting the text into lines
    lines = allText.split('\n')

    fname = ''

    # obtaining full name
    for line in lines:
        if "Фамилия, имя, отчество" in line:
            fname = line.replace('Фамилия, имя, отчество', ' ')
            fname = re.sub('[^а-яА-Я]+', ' ', fname)
            fname = ' '.join(fname.split(' '))
            break

    oSel.setString("")

    # resolving issues with -
    problems = re.findall('[а-яА-Я]+-\s[а-яА-Я]+', selectedText)
    for word in problems:
        upd = re.sub("-\s", '', word)
        selectedText = selectedText.replace(word, upd)

    # sending the request to server
    toSend = {'fname': fname, "text": selectedText}
    data = json.dumps(toSend).encode("utf8")
    url = 'http://localhost:8080/send'
    req = urllib.request.Request(url, data=data, headers={'content-type': 'application/json'})

    # transforming response to json
    res = urllib.request.urlopen(req)
    res_body = res.read()
    j = json.loads(res_body.decode("utf-8"))

    # change font size
    # cursor.setPropertyValue("CharHeight", 40)

    # updating the selected text
    # oSel.setString(j['text'])

    cursor = oSel.Text.createTextCursorByRange(oSel)
    resText = j['text']
    changes = j['colored']  # [(3, 14), ]

    curInd = 0
    for start, end in changes:
        if curInd <= start:
            cursor.setPropertyValue('CharColor', 0)
            startText.insertString(cursor, resText[curInd:start], False)
            cursor.setPropertyValue('CharColor', 255)
            startText.insertString(cursor, resText[start:end], False)
            curInd = end

    if curInd < len(resText):
        cursor.setPropertyValue('CharColor', 0)
        startText.insertString(cursor, resText[curInd:], False)

    return