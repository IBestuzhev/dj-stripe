"""
.. module:: dj-stripe.tests.test_transfer
   :synopsis: dj-stripe Transfer Model Tests.

.. moduleauthor:: Alex Kavanaugh (@kavdev)

"""
import decimal
from copy import deepcopy
from unittest.mock import patch

from django.test.testcases import TestCase

from djstripe.models import Event, Transfer

from . import FAKE_EVENT_TRANSFER_CREATED


class TransferTest(TestCase):

    @patch('stripe.Transfer.retrieve')
    @patch("stripe.Event.retrieve")
    def test_update_transfer(self, event_retrieve_mock, transfer_retrieve_mock):
        fake_event_created = deepcopy(FAKE_EVENT_TRANSFER_CREATED)

        fake_event_updated = deepcopy(fake_event_created)
        fake_event_updated.update({"id": "evt_000000000000000000000000"})
        fake_event_updated.update({"type": "transfer.updated"})
        fake_event_updated["data"]["object"]["amount"] = 3057
        fake_event_updated["data"]["object"]["source_type"] = "fish"

        event_retrieve_mock.side_effect = [fake_event_created, fake_event_updated]
        transfer_retrieve_mock.side_effect = [
            fake_event_created["data"]["object"],
            fake_event_updated["data"]["object"]
        ]

        # Create transfer
        created_event = Event.sync_from_stripe_data(fake_event_created)
        created_event.invoke_webhook_handlers()

        # Signal a transfer update
        updated_event = Event.sync_from_stripe_data(fake_event_updated)
        updated_event.invoke_webhook_handlers()

        transfer_instance = Transfer.objects.get(source_type="fish")
        self.assertEqual(2, transfer_retrieve_mock.call_count)

        # Test to string to ensure data was updated
        self.assertEqual("<amount={amount}, id={id}>".format(
            amount=fake_event_updated["data"]["object"]["amount"] / decimal.Decimal("100"),
            id=fake_event_updated["data"]["object"]["id"]
        ), str(transfer_instance))
