from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from movie.models import Genre
from movie.views import fetch_omdb


class GenreModelTests(TestCase):
    def test_slug_is_created_from_title(self):
        genre = Genre.objects.create(title='Science Fiction')
        self.assertEqual(genre.slug, 'science-fiction')


class OmdbClientTests(TestCase):
    @override_settings(OMDB_API_KEY='')
    def test_missing_key_returns_safe_error(self):
        result = fetch_omdb(s='Arrival')
        self.assertEqual(result['Response'], 'False')
        self.assertIn('not configured', result['Error'])

    @override_settings(OMDB_API_KEY='test-key')
    @patch('movie.views.requests.get')
    def test_request_uses_settings_key_and_timeout(self, mock_get):
        response = Mock()
        response.json.return_value = {'Response': 'True', 'Search': []}
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        result = fetch_omdb(s='Arrival')

        self.assertEqual(result['Response'], 'True')
        mock_get.assert_called_once_with(
            'https://www.omdbapi.com/',
            params={'apikey': 'test-key', 's': 'Arrival'},
            timeout=10,
        )
