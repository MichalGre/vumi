"""Tests for go.components.message_store_migrators."""

from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase

from vumi.tests.utils import PersistenceMixin, import_skip
from vumi.tests.helpers import MessageHelper

try:
    from vumi.components.tests.message_store_old_models import (
        OutboundMessageVNone, InboundMessageVNone, BatchVNone)
    from vumi.components.message_store import (
        OutboundMessage as OutboundMessageV1,
        InboundMessage as InboundMessageV1)
    riak_import_error = None
except ImportError, e:
    riak_import_error = e


class TestMigratorBase(TestCase, PersistenceMixin):
    timeout = 5
    use_riak = True

    @inlineCallbacks
    def setUp(self):
        yield self._persist_setUp()
        if riak_import_error is not None:
            import_skip(riak_import_error, 'riakasaurus', 'riakasaurus.riak')
        self.manager = self.get_riak_manager()
        self.msg_helper = MessageHelper()

    def tearDown(self):
        return self._persist_tearDown()


class OutboundMessageMigratorTestCase(TestMigratorBase):
    @inlineCallbacks
    def setUp(self):
        yield super(OutboundMessageMigratorTestCase, self).setUp()
        self.outbound_vnone = self.manager.proxy(OutboundMessageVNone)
        self.outbound_v1 = self.manager.proxy(OutboundMessageV1)
        self.batch_vnone = self.manager.proxy(BatchVNone)

    @inlineCallbacks
    def test_migrate_vnone_to_v1(self):
        msg = self.msg_helper.make_outbound("outbound")
        old_batch = self.batch_vnone(key=u"batch-1")
        old_record = self.outbound_vnone(msg["message_id"],
                                         msg=msg, batch=old_batch)
        yield old_record.save()
        new_record = yield self.outbound_v1.load(old_record.key)
        self.assertEqual(new_record.msg, msg)
        self.assertEqual(new_record.batches.keys(), [old_batch.key])

    @inlineCallbacks
    def test_migrate_vnone_to_v1_without_batch(self):
        msg = self.msg_helper.make_outbound("outbound")
        old_record = self.outbound_vnone(msg["message_id"],
                                         msg=msg, batch=None)
        yield old_record.save()
        new_record = yield self.outbound_v1.load(old_record.key)
        self.assertEqual(new_record.msg, msg)
        self.assertEqual(new_record.batches.keys(), [])


class InboundMessageMigratorTestCase(TestMigratorBase):

    @inlineCallbacks
    def setUp(self):
        yield super(InboundMessageMigratorTestCase, self).setUp()
        self.inbound_vnone = self.manager.proxy(InboundMessageVNone)
        self.inbound_v1 = self.manager.proxy(InboundMessageV1)
        self.batch_vnone = self.manager.proxy(BatchVNone)

    @inlineCallbacks
    def test_migrate_vnone_to_v1(self):
        msg = self.msg_helper.make_inbound("inbound")
        old_batch = self.batch_vnone(key=u"batch-1")
        old_record = self.inbound_vnone(msg["message_id"],
                                        msg=msg, batch=old_batch)
        yield old_record.save()
        new_record = yield self.inbound_v1.load(old_record.key)
        self.assertEqual(new_record.msg, msg)
        self.assertEqual(new_record.batches.keys(), [old_batch.key])

    @inlineCallbacks
    def test_migrate_vnone_to_v1_without_batch(self):
        msg = self.msg_helper.make_inbound("inbound")
        old_record = self.inbound_vnone(msg["message_id"],
                                        msg=msg, batch=None)
        yield old_record.save()
        new_record = yield self.inbound_v1.load(old_record.key)
        self.assertEqual(new_record.msg, msg)
        self.assertEqual(new_record.batches.keys(), [])
