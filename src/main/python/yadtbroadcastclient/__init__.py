from __future__ import absolute_import

import os
import logging
import yaml

from twisted.internet import reactor

from autobahn.wamp import WampClientFactory, WampClientProtocol
 

class WampBroadcaster(object):
    def __init__(self, host, port, target=None):
        self.host = host
        self.port = port
        self.target = target
        self.url = 'ws://%s:%s/' % (self.host, self.port)
        self.factory = None
        self.client = None
        self.logger = logging.getLogger('broadcaster')
        self.logger.info('using %s for publishing' % self.url)
        self.on_session_open_handlers = []

    def connect(self):
        if self.client:
            return
        broadcaster = self
        self.logger.debug('trying to connect to %s' % self.url)
        class BroadcastClientProtocol(WampClientProtocol):
            def onSessionOpen(self):
                broadcaster.client = self
                broadcaster.logger.info('connected to broadcast-server %s' % broadcaster.url)
                broadcaster.onSessionOpen()

        self.factory = WampClientFactory(self.url)
        self.factory.protocol = BroadcastClientProtocol
        reactor.connectTCP(self.host, self.port, self.factory)

    def addOnSessionOpenHandler(self, handler):
        self.on_session_open_handlers.append(handler)

    def onSessionOpen(self):
        if self.target:
            self.client.subscribe(self.target, self.onEvent)
        for handler in self.on_session_open_handlers:
            handler()

    def onEvent(self, target, event):
        pass

    # TODO: unify old and new send calls
    def sendFullUpdate(self, data):
        return self._sendEvent('full-update', data)

    # TODO: unify old and new send calls
    def sendServiceChange(self, data):
        return self._sendEvent('service-change', data)

    # TODO: unify old and new send calls
    def _sendEvent(self, id, data):
        if not self.client:
            key = 'not_connected_warning_sent'
            if not getattr(self, key, False):
                setattr(self, key, True)
                self.logger.warning('could not connect to broadcaster %s' % self.url)

            self.logger.debug('not connected, dropping data: %s' % data)
            return
        self.client.publish(self.target, {
            'type': 'event',
            'id': id,
            'target': self.target,
            'payload' : data
        })


    # TODO: unify old and new send calls
    def _check_connection(self):
        if not self.client:
            key = 'not_connected_warning_sent'
            if not getattr(self, key, False):
                setattr(self, key, True)
                self.logger.warning('could not connect to broadcaster %s' % self.url)
            self.logger.debug('not connected, dropping data...')
            return False
        return True

    # TODO: unify old and new send calls
    def publish_cmd_for_target(self, target, cmd, state, message=None):
        if not self._check_connection():
            return
        self.client.publish(target, {
            'type': 'event',
            'id': 'cmd',
            'cmd': cmd,
            'state': state,
            'message': message
        })

    # TODO: unify old and new send calls
    def publish_cmd(self, cmd, state, message=None):
        return self.publish_cmd_for_target(self.target, cmd, state, message)

    # TODO: unify old and new send calls
    def publish_request_for_target(self, target, cmd, args):
        if not self._check_connection():
            return
        self.client.publish(target, {
            'type': 'event',
            'id': 'request',
            'cmd': cmd,
            'args': args
        })



