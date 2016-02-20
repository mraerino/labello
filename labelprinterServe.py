#!/usr/bin/env python2
# coding: utf-8
# https://fragments.turtlemeat.com/pythonwebserver.php
import string
import cgi
import time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import labelprinterServeConf as conf


class MyHandler(BaseHTTPRequestHandler):

    def printText(
            self,
            txt,
            charSize='42',
            font='lettergothic',
            align='left',
            bold='off',
            charStyle='normal',
            cut='full'
    ):
        print "start printing:", txt
        import socket
        from brotherprint import BrotherPrint

        f_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        f_socket.connect((conf.printerIp, conf.printerPort))
        printjob = BrotherPrint(f_socket)

        printjob.command_mode()
        printjob.initialize()
        printjob.select_font(font)
        printjob.char_size(charSize)  # 28 chars
        printjob.alignment(align)
        printjob.bold(bold)
        printjob.char_style(charStyle)
        printjob.cut_setting(cut)

        printjob.send(txt.decode('utf8').encode('iso-8859-1'))
        printjob.print_page('full')

    def getCmbFromList(self, ls):
        cmb = ''
        for itm in ls:
            cmb += '<option value="' + str(itm) + '">' + str(itm) + '</option>'
        return cmb

    def getPolymerFromList(self, ls):
        poly = '';
        for itm in ls:
            poly += '<paper-item>' + str(itm) + '</paper-item>'
        return poly

    def do_GET(self):
        try:
            sizesOutline = [
                '24',
                '32',
                '48'
            ]

            sizesBitmap = [
                '42',
                #'24',
                #'32',
                #'48',
                '11',
                '33',
                '38',
                '44',
                '46',
                '50',
                '58',
                '67',
                '75',
                '77',
                '83',
                '92',
                '100',
                '111',
                '117',
                '133',
                '144',
                '150',
                '167',
                '200',
                '233',
            ]

            sizesCmb = '<optgroup label="Bitmap Sizes">'
            sizesCmb += self.getCmbFromList(sizesBitmap)
            sizesCmb += '</optgroup>'

            sizesCmb += '<optgroup label="Outline Sizes">'
            sizesCmb += self.getCmbFromList(sizesOutline)
            sizesCmb += '</optgroup>'

            sizesPoly = self.getPolymerFromList(sizesOutline + sizesBitmap)

            fontsOutline = [
                'lettergothic',
                'brusselsoutline',
                'helsinkioutline'
            ]

            fontsBitMap = [
                'brougham',
                'lettergothicbold',
                'brusselsbit',
                'helsinkibit',
                'sandiego'
            ]

            fontsCmb = '<optgroup label="Outline Fonts">'
            fontsCmb += self.getCmbFromList(fontsOutline)
            fontsCmb += '</optgroup>'

            fontsCmb += '<optgroup label="Bitmap Fonts">'
            fontsCmb += self.getCmbFromList(fontsBitMap)
            fontsCmb += '</optgroup>'

            fontsPoly = '<polymer-item disabled>Outline Fonts</polymer-item>'
            fontsPoly += self.getPolymerFromList(fontsOutline)

            fontsPoly += '<polymer-item disabled>Bitmap Fonts</polymer-item>'
            fontsPoly += self.getPolymerFromList(fontsBitMap)

            aligns = [
                'left',
                'center',
                'right',
                'justified'
            ]
            alignsCmb = self.getCmbFromList(aligns)
            alignsPoly = self.getPolymerFromList(aligns)

            charStyles = [
                'normal',
                'outline',
                'shadow',
                'outlineshadow'
            ]
            charStylesCmb = self.getCmbFromList(charStyles)
            charStylePoly = self.getPolymerFromList(charStyles)

            cuts = [
                'full',
                'half',
                'chain',
                'special'
            ]
            cutsCmb = self.getCmbFromList(cuts)
            cutsPoly = self.getPolymerFromList(cuts)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            template = ''
            if self.path == '/':
                template = open('templates/base.html').read()
            elif self.path == '/magic':
                template = open('templates/magic.html').read()
            else:
                template = 'NOTHING'

            template = template.replace('{{sizesCmb}}', sizesCmb)
            template = template.replace('{{sizesPoly}}', sizesPoly)
            template = template.replace('{{fontsCmb}}', fontsCmb)
            template = template.replace('{{fontsPoly}}', fontsPoly)
            template = template.replace('{{alignsCmb}}', alignsCmb)
            template = template.replace('{{alignsPoly}}', alignsPoly)
            template = template.replace('{{charStylesCmb}}', charStylesCmb)
            template = template.replace('{{charStylePoly}}', charStylePoly)
            template = template.replace('{{cutsCmb}}', cutsCmb)
            template = template.replace('{{cutsPoly}}', cutsPoly)

            self.wfile.write(template)

            return

        except Exception as ex:
            self.send_error(404, 'File Not Found: {} {}'.format(self.path, ex))

    def do_POST(self):
        self.send_response(301)
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            print ctype, pdict
            query = None

            if ctype == 'multipart/form-data':
                query = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                query = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)

            print query
            self.end_headers()
            text = query.get('text')

            finalTxt = ''
            print text
            for txt in text:
                finalTxt += txt

            self.wfile.write("POST OK.\n")
            self.wfile.write("start printing: " + finalTxt + "\n")

            print finalTxt

            self.printText(
                finalTxt,
                charSize=query.get('fontSize', [42])[0],
                font=query.get('font', ['lettergothic'])[0],
                align=query.get('align', ['left'])[0],
                bold=query.get('bold', ['off'])[0],
                charStyle=query.get('charStyle', ['normal'])[0],
                cut=query.get('cut', ['full'])[0],
            )
        except Exception as ex:
            print 'ERROR:', ex
            self.wfile.write("ERROR: " + str(ex))


def main():
    server = None
    try:
        server = HTTPServer(('', conf.serverPort), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        if server is not None:
            server.socket.close()

if __name__ == '__main__':
    main()
