import unittest

from mock import Mock, call

from yadtbroadcastclient import WampBroadcaster


class YadtBroadcastClientTests(unittest.TestCase):

    def test_publish_cmd_for_target_should_publish_expected_event(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.client = Mock()

        WampBroadcaster.publish_cmd_for_target(mock_broadcaster,
                                               'target', 'some-cmd', 'destroyed',
                                               'hello', 'nsa-tracker')

        mock_broadcaster.client.publish.assert_called_with('target',
                                                           {
                                                               'cmd': 'some-cmd',
                                                               'state': 'destroyed',
                                                               'tracking_id': 'nsa-tracker',
                                                               'message': 'hello',
                                                               'type': 'event',
                                                               'id': 'cmd'
                                                           })

    def test_sendFullUpdate_should_forward_tracking_id_to_sendEvent(self):
        mock_broadcaster = Mock(WampBroadcaster)

        WampBroadcaster.sendFullUpdate(
            mock_broadcaster, 'data', tracking_id='tracking-id')

        self.assertEqual(
            call('full-update', 'data', 'tracking-id'), mock_broadcaster._sendEvent.call_args)

    def test_sendServiceChange_should_forward_tracking_id_to_sendEvent(self):
        mock_broadcaster = Mock(WampBroadcaster)

        WampBroadcaster.sendServiceChange(
            mock_broadcaster, 'data', tracking_id='tracking-id')

        self.assertEqual(
            call('service-change', 'data', 'tracking-id'), mock_broadcaster._sendEvent.call_args)

    def test_publish_cmd_should_forward_tracking_id_to_publish_cmd_for_target(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.target = 'target'

        WampBroadcaster.publish_cmd(
            mock_broadcaster, 'command', 'state', message='message', tracking_id='tracking-id')

        actual_call = mock_broadcaster.publish_cmd_for_target.call_args
        self.assertEqual(
            call('target', 'command', 'state', 'message', 'tracking-id'), actual_call)

    def test_sendEvent_should_publish_expected_event_on_default_target(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.target = 'broadcaster-target'
        mock_broadcaster.logger = Mock()
        mock_broadcaster.client = Mock()

        WampBroadcaster._sendEvent(
            mock_broadcaster, 'event-id', 'event-data', tracking_id='tracking-id')

        actual_call = mock_broadcaster.client.publish.call_args
        self.assertEqual(call('broadcaster-target', {'payload': 'event-data',
                                                     'type': 'event',
                                                     'id': 'event-id',
                                                     'tracking_id': 'tracking-id',
                                                     'target': 'broadcaster-target'}
                              ), actual_call)

    def test_sendEvent_on_target_should_publish_expected_event(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.target = 'broadcaster-target'
        mock_broadcaster.logger = Mock()
        mock_broadcaster.client = Mock()

        WampBroadcaster._sendEvent(mock_broadcaster,
                                   'event-id',
                                   'event-data',
                                   tracking_id='tracking-id',
                                   target='target')

        actual_call = mock_broadcaster.client.publish.call_args
        self.assertEqual(call('target', {'payload': 'event-data',
                                         'type': 'event',
                                         'id': 'event-id',
                                         'tracking_id': 'tracking-id',
                                         'target': 'target'}
                              ), actual_call)


class ConnectionCheckTests(unittest.TestCase):

    def test_check_connection_should_return_false_when_link_is_down(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.logger = Mock()
        mock_broadcaster.url = "ws://broadcaster"
        mock_broadcaster.client = None

        self.assertEqual(
            WampBroadcaster._check_connection(mock_broadcaster), False)
        self.assertTrue(
            hasattr(mock_broadcaster, "not_connected_warning_sent"))

    def test_check_connection_should_return_true_when_link_is_up(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.logger = Mock()
        mock_broadcaster.url = "ws://broadcaster"
        mock_broadcaster.client = Mock()

        self.assertEqual(
            WampBroadcaster._check_connection(mock_broadcaster), True)
        self.assertFalse(
            hasattr(mock_broadcaster, "not_connected_warning_sent"))
