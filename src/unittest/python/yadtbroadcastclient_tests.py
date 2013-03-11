import unittest

from mock import Mock, call

from yadtbroadcastclient import WampBroadcaster


class YadtBroadcastClientTests(unittest.TestCase):

    def test_sendFullUpdate_should_forward_tracking_id_to_sendEvent(self):
        mock_broadcaster = Mock(WampBroadcaster)

        WampBroadcaster.sendFullUpdate(mock_broadcaster, 'data', tracking_id='tracking-id')

        self.assertEqual(call('full-update', 'data', 'tracking-id'), mock_broadcaster._sendEvent.call_args)

    def test_sendServiceChange_should_forward_tracking_id_to_sendEvent(self):
        mock_broadcaster = Mock(WampBroadcaster)

        WampBroadcaster.sendServiceChange(mock_broadcaster, 'data', tracking_id='tracking-id')

        self.assertEqual(call('service-change', 'data', 'tracking-id'), mock_broadcaster._sendEvent.call_args)