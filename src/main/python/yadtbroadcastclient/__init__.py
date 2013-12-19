from __future__ import absolute_import

import logging

from twisted.internet import reactor

from autobahn.wamp import WampClientFactory, WampClientProtocol


class WampBroadcaster(object):
    HEARTBEAT_INTERVAL = 120

    def __init__(self, host, port, target=None):
        self.host = host
        self.port = port
        self.target = target
        self.url = 'ws://%s:%s/' % (self.host, self.port)
        self.factory = None
        self.client = None
        self.logger = logging.getLogger('broadcaster')
        self.logger.info('going to use %s for publishing' % self.url)
        self.on_session_open_handlers = []

    def connect(self):
        if self.client:
            self.logger.debug('already connected to %s' % self.url)
            return
        broadcaster = self
        self.logger.debug('trying to connect to %s' % self.url)

        class BroadcastClientProtocol(WampClientProtocol):

            def onSessionOpen(self):
                broadcaster.client = self
                broadcaster.logger.info(
                    'connected to broadcast-server %s' % broadcaster.url)
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
        reactor.callLater(WampBroadcaster.HEARTBEAT_INTERVAL, self._heartbeat)

    def _heartbeat(self):
        self._sendEvent('heartbeat', None)
        reactor.callLater(WampBroadcaster.HEARTBEAT_INTERVAL, self._heartbeat)

    def onEvent(self, target, event):
        pass

    def sendFullUpdate(self, data, tracking_id=None):
        return self._sendEvent('full-update', data, tracking_id)

    def sendServiceChange(self, data, tracking_id=None):
        return self._sendEvent('service-change', data, tracking_id)

    def _sendEvent(self, id, data, tracking_id=None, target=None, **kwargs):
        if not target:
            target = self.target
        self.logger.debug('Going to send event %s on target %r' % (id, target))

        if not self._check_connection():
            return

        event = {
            'type': 'event',
            'id': id,
            'tracking_id': tracking_id,
            'target': target,
            'payload': data
        }
        for kwarg_key, kwarg_val in kwargs.iteritems():
            event[kwarg_key] = kwarg_val

        self.client.publish(target, event)

    def _check_connection(self):
        if not self.client:
            key = 'not_connected_warning_sent'
            if not getattr(self, key, False):
                setattr(self, key, True)
                self.logger.warning(
                    'could not connect to broadcaster %s' % self.url)
            self.logger.debug('not connected, dropping data...')
            return False
        return True

    def publish_cmd_for_target(self, target, cmd, state, message=None, tracking_id=None):
        self._sendEvent(id='cmd',
                        data=None,
                        tracking_id=tracking_id,
                        target=target,
                        cmd=cmd,
                        state=state,
                        message=message)

    def publish_cmd(self, cmd, state, message=None, tracking_id=None):
        self._sendEvent(id='cmd',
                        data=None,
                        tracking_id=tracking_id,
                        target=self.target,
                        cmd=cmd,
                        state=state,
                        message=message)

    def publish_request_for_target(self, target, cmd, args, tracking_id=None):
        self._sendEvent(id='request',
                        data=None,
                        tracking_id=tracking_id,
                        target=target,
                        cmd=cmd,
                        args=args)
