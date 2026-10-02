import unittest
from unittest.mock import Mock
import requests
import social_scanner as scanner

class ScannerTests(unittest.TestCase):
    def response(self, body):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.iter_content.return_value = [body]
        return Mock(get=Mock(return_value=response))

    def test_rss_missing_title_and_whitespace(self):
        client = self.response(b'<rss><channel><item/><item><title> hello \n world </title></item></channel></rss>')
        self.assertEqual(scanner.get_rss('url','RSS',session=client), ['[RSS] hello world'])
        client.get.return_value.raise_for_status.assert_called_once()

    def test_atom(self):
        client = self.response(b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>News</title></entry></feed>')
        self.assertEqual(scanner.get_rss('url','Atom',session=client), ['[Atom] News'])

    def test_http_and_xml_errors_are_explicit_and_redacted(self):
        client = Mock(get=Mock(side_effect=requests.Timeout('secret-token')))
        with self.assertRaisesRegex(scanner.FeedError, 'unavailable') as result:
            scanner.get_rss('url','RSS',session=client)
        self.assertNotIn('secret-token', str(result.exception))
        for body in [b'<invalid', b'<html/>', b'<!DOCTYPE rss><rss/>', b'x'*(scanner.MAX_FEED_BYTES+1)]:
            with self.assertRaises(scanner.FeedError):
                scanner.get_rss('url','RSS',session=self.response(body))

    def test_telegram_success_and_failures(self):
        client = Mock(); client.post.return_value.json.return_value = {'ok': True}
        scanner.send_telegram('hello','test-token','id',client)
        self.assertEqual(client.post.call_args.kwargs['timeout'], scanner.TIMEOUT)
        client.post.return_value.json.return_value = {'ok': False}
        with self.assertRaises(scanner.FeedError): scanner.send_telegram('hello','test-token','id',client)
        client.post.side_effect = requests.Timeout('test-token')
        with self.assertRaisesRegex(scanner.FeedError, '^Telegram delivery failed$'):
            scanner.send_telegram('hello','test-token','id',client)

if __name__ == '__main__': unittest.main()
