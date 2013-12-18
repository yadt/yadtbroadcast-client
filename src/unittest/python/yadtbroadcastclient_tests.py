import unittest

from mock import Mock, call, patch

from yadtbroadcastclient import WampBroadcaster


class YadtBroadcastClientTests(unittest.TestCase):

    def test_should_publish_request_for_target(self):

        ybc = WampBroadcaster('host', 42)
        ybc.target = 'broadcaster-target'
        ybc.logger = Mock()
        ybc.client = Mock()

        ybc.publish_request_for_target('target', 'cmd', 'args', 'nsa-tracker')

        ybc.client.publish.assert_called_with('target',
                                              {
                                                  'args': 'args',
                                                  'cmd': 'cmd',
                                                  'type': 'event',
                                                  'id': 'request',
                                                  'payload': None,
                                                  'target': 'target',
                                                  'tracking_id': 'nsa-tracker'})

    def test_should_publish_cmd_for_default_target(self):
        ybc = WampBroadcaster('host', 42)
        ybc.target = 'broadcaster-target'
        ybc.logger = Mock()
        ybc.client = Mock()

        ybc.publish_cmd('status', 'failed', 'hello', 'nsa-tracking')

        ybc.client.publish.assert_called_with('broadcaster-target', {
            'cmd': 'status',
            'state': 'failed',
            'payload': None,
            'tracking_id': 'nsa-tracking',
            'message': 'hello',
            'type': 'event',
            'target': 'broadcaster-target',
            'id': 'cmd'})

    def test_should_publish_cmd_for_target(self):
        ybc = WampBroadcaster('host', 42)
        ybc.target = 'broadcaster-target'
        ybc.logger = Mock()
        ybc.client = Mock()

        ybc.publish_cmd_for_target(
            'target', 'status', 'failed', 'hello', 'nsa-tracking')

        ybc.client.publish.assert_called_with('target', {
            'cmd': 'status',
            'state': 'failed',
            'payload': None,
            'tracking_id': 'nsa-tracking',
            'message': 'hello',
            'type': 'event',
            'target': 'target',
            'id': 'cmd'})

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

    def test_sendEvent_should_use_kwargs_as_event_items(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.target = 'broadcaster-target'
        mock_broadcaster.logger = Mock()
        mock_broadcaster.client = Mock()

        WampBroadcaster._sendEvent(mock_broadcaster,
                                   'event-id',
                                   'event-data',
                                   tracking_id='tracking-id',
                                   target='target',
                                   state='foobar',
                                   bar='baz')

        actual_call = mock_broadcaster.client.publish.call_args
        self.assertEqual(call('target', {'payload': 'event-data',
                                         'type': 'event',
                                         'id': 'event-id',
                                         'tracking_id': 'tracking-id',
                                         'target': 'target',
                                         'state': 'foobar',
                                         'bar': 'baz'}
                              ), actual_call)

    @patch('yadtbroadcastclient.WampBroadcaster._check_connection')
    def test_sendEvent_should_drop_data_when_no_connection(self, check_connection):
        check_connection.return_value = False
        ybc = WampBroadcaster('host', 42)
        ybc.target = 'broadcaster-target'
        ybc.logger = Mock()
        ybc.client = Mock()

        WampBroadcaster._sendEvent(ybc,
                                   'event-id',
                                   'event-data',
                                   tracking_id='tracking-id',
                                   target='target')

        self.assertFalse(ybc.client.publish.called)

    @patch('yadtbroadcastclient.WampBroadcaster._check_connection')
    def test_sendEvent_should_not_drop_data_when_connection(self, check_connection):
        check_connection.return_value = True
        ybc = WampBroadcaster('host', 42)
        ybc.target = 'broadcaster-target'
        ybc.logger = Mock()
        ybc.client = Mock()

        WampBroadcaster._sendEvent(ybc,
                                   'event-id',
                                   'event-data',
                                   tracking_id='tracking-id',
                                   target='target')

        self.assertTrue(ybc.client.publish.called)


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
