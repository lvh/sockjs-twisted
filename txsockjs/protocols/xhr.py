# Copyright (c) 2012, Christopher Gamble
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Christopher Gamble nor the names of its 
#      contributors may be used to endorse or promote products derived 
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

from txsockjs.protocols.base import SessionProtocol

class XHR(SessionProtocol):
    allowedMethods = ['OPTIONS','POST']
    contentType = 'application/javascript; charset=UTF-8'
    chunked = False
    written = False
    def write(self, data):
        if self.written:
            self.wrappedProtocol.requeue([data])
            return
        packet = "%s\n" % data
        SessionProtocol.write(self, packet)
        self.written = True
        self.loseConnection()
    def writeSequence(self, data):
        if not self.written:
            self.write(data.pop(0))
        self.wrappedProtocol.requeue(data)

class XHRSend(SessionProtocol):
    allowedMethods = ['OPTIONS','POST']
    contentType = 'text/plain; charset=UTF-8'
    writeOnly = True
    def sendHeaders(self, headers = {}):
        h = {'status': '204 No Body'}
        h.update(headers)
        SessionProtocol.sendHeaders(self, h)

class XHRStream(SessionProtocol):
    allowedMethods = ['OPTIONS','POST']
    contentType = 'application/javascript; charset=UTF-8'
    sent = 0
    def prepConnection(self):
        self.sendHeaders()
        SessionProtocol.write(self, 'h'*2048+"\n")
    def write(self, data):
        packet = "%s\n" % data
        self.sent += len(packet)
        SessionProtocol.write(self, packet)
        if self.sent > self.factory.options['streaming_limit']:
            self.loseConnection()
    def writeSequence(self, data):
        for d in data:
            self.write(d)
