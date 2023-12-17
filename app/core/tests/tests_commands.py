"""
Test custom Django managementcommands.
"""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waitng for database ready to use"""
        patched_check.return_value = True

        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_sb_delay(self, patched_sleep, patched_check):
        """Test waiting for db when getting error"""
        errors_sequence = [Psycopg2Error] * 3 + [OperationalError] * 9 + [True]
        patched_check.side_effect = errors_sequence

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, len(errors_sequence))
        patched_check.assert_called_with(databases=['default'])
