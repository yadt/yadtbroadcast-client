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

    def test_publish_cmd_should_forward_tracking_id_to_publish_cmd_for_target(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.target = 'target'

        WampBroadcaster.publish_cmd(mock_broadcaster, 'command', 'state', message='message', tracking_id='tracking-id')

        actual_call = mock_broadcaster.publish_cmd_for_target.call_args
        self.assertEqual(call('target', 'command', 'state', 'message', 'tracking-id'), actual_call)

    def test_sendEvent_should_publish_expected_event(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.target = 'target'
        mock_broadcaster.logger = Mock()
        mock_broadcaster.client = Mock()

        WampBroadcaster._sendEvent(mock_broadcaster, 'event-id', 'event-data', tracking_id='tracking-id')

        actual_call = mock_broadcaster.client.publish.call_args
        self.assertEqual(call('target', {'payload': 'event-data',
                                         'type': 'event',
                                         'id': 'event-id',
                                         'tracking_id': 'tracking-id',
                                         'target': 'target'}
                              ), actual_call)
