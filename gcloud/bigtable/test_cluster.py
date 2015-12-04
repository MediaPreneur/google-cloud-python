# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest2


class TestCluster(unittest2.TestCase):

    def _getTargetClass(self):
        from gcloud.bigtable.cluster import Cluster
        return Cluster

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_constructor_defaults(self):
        zone = 'zone'
        cluster_id = 'cluster-id'
        client = object()

        cluster = self._makeOne(zone, cluster_id, client)
        self.assertEqual(cluster.zone, zone)
        self.assertEqual(cluster.cluster_id, cluster_id)
        self.assertEqual(cluster.display_name, cluster_id)
        self.assertEqual(cluster.serve_nodes, 3)
        self.assertTrue(cluster._client is client)

    def test_constructor_non_default(self):
        zone = 'zone'
        cluster_id = 'cluster-id'
        display_name = 'display_name'
        serve_nodes = 8
        client = object()

        cluster = self._makeOne(zone, cluster_id, client,
                                display_name=display_name,
                                serve_nodes=serve_nodes)
        self.assertEqual(cluster.zone, zone)
        self.assertEqual(cluster.cluster_id, cluster_id)
        self.assertEqual(cluster.display_name, display_name)
        self.assertEqual(cluster.serve_nodes, serve_nodes)
        self.assertTrue(cluster._client is client)

    def test_table_factory(self):
        from gcloud.bigtable.table import Table

        zone = 'zone'
        cluster_id = 'cluster-id'
        cluster = self._makeOne(zone, cluster_id, None)

        table_id = 'table_id'
        table = cluster.table(table_id)
        self.assertTrue(isinstance(table, Table))
        self.assertEqual(table.table_id, table_id)
        self.assertEqual(table._cluster, cluster)

    def test_from_pb_success(self):
        from gcloud.bigtable._generated import (
            bigtable_cluster_data_pb2 as data_pb2)

        project = 'PROJECT'
        zone = 'zone'
        cluster_id = 'cluster-id'
        client = _Client(project=project)

        cluster_name = ('projects/' + project + '/zones/' + zone +
                        '/clusters/' + cluster_id)
        cluster_pb = data_pb2.Cluster(
            name=cluster_name,
            display_name=cluster_id,
            serve_nodes=3,
        )

        klass = self._getTargetClass()
        cluster = klass.from_pb(cluster_pb, client)
        self.assertTrue(isinstance(cluster, klass))
        self.assertEqual(cluster._client, client)
        self.assertEqual(cluster.zone, zone)
        self.assertEqual(cluster.cluster_id, cluster_id)

    def test_from_pb_bad_cluster_name(self):
        from gcloud.bigtable._generated import (
            bigtable_cluster_data_pb2 as data_pb2)

        cluster_name = 'INCORRECT_FORMAT'
        cluster_pb = data_pb2.Cluster(name=cluster_name)

        klass = self._getTargetClass()
        with self.assertRaises(ValueError):
            klass.from_pb(cluster_pb, None)

    def test_from_pb_project_mistmatch(self):
        from gcloud.bigtable._generated import (
            bigtable_cluster_data_pb2 as data_pb2)

        project = 'PROJECT'
        zone = 'zone'
        cluster_id = 'cluster-id'
        alt_project = 'ALT_PROJECT'
        client = _Client(project=alt_project)

        self.assertNotEqual(project, alt_project)

        cluster_name = ('projects/' + project + '/zones/' + zone +
                        '/clusters/' + cluster_id)
        cluster_pb = data_pb2.Cluster(name=cluster_name)

        klass = self._getTargetClass()
        with self.assertRaises(ValueError):
            klass.from_pb(cluster_pb, client)

    def test_name_property(self):
        project = 'PROJECT'
        zone = 'zone'
        cluster_id = 'cluster-id'
        client = _Client(project=project)

        cluster = self._makeOne(zone, cluster_id, client)
        cluster_name = ('projects/' + project + '/zones/' + zone +
                        '/clusters/' + cluster_id)
        self.assertEqual(cluster.name, cluster_name)

    def test___eq__(self):
        zone = 'zone'
        cluster_id = 'cluster_id'
        client = object()
        cluster1 = self._makeOne(zone, cluster_id, client)
        cluster2 = self._makeOne(zone, cluster_id, client)
        self.assertEqual(cluster1, cluster2)

    def test___eq__type_differ(self):
        cluster1 = self._makeOne('zone', 'cluster_id', 'client')
        cluster2 = object()
        self.assertNotEqual(cluster1, cluster2)

    def test___ne__same_value(self):
        zone = 'zone'
        cluster_id = 'cluster_id'
        client = object()
        cluster1 = self._makeOne(zone, cluster_id, client)
        cluster2 = self._makeOne(zone, cluster_id, client)
        comparison_val = (cluster1 != cluster2)
        self.assertFalse(comparison_val)

    def test___ne__(self):
        cluster1 = self._makeOne('zone1', 'cluster_id1', 'client1')
        cluster2 = self._makeOne('zone2', 'cluster_id2', 'client2')
        self.assertNotEqual(cluster1, cluster2)

    def test_reload(self):
        from gcloud.bigtable._generated import (
            bigtable_cluster_data_pb2 as data_pb2)
        from gcloud.bigtable._generated import (
            bigtable_cluster_service_messages_pb2 as messages_pb2)
        from gcloud.bigtable._testing import _FakeStub
        from gcloud.bigtable.cluster import _DEFAULT_SERVE_NODES

        project = 'PROJECT'
        zone = 'zone'
        cluster_id = 'cluster-id'
        timeout_seconds = 123

        client = _Client(project, timeout_seconds=timeout_seconds)
        cluster = self._makeOne(zone, cluster_id, client)

        # Create request_pb
        cluster_name = ('projects/' + project + '/zones/' + zone +
                        '/clusters/' + cluster_id)
        request_pb = messages_pb2.GetClusterRequest(name=cluster_name)

        # Create response_pb
        serve_nodes = 31
        display_name = u'hey-hi-hello'
        response_pb = data_pb2.Cluster(
            display_name=display_name,
            serve_nodes=serve_nodes,
        )

        # Patch the stub used by the API method.
        client._cluster_stub = stub = _FakeStub(response_pb)

        # Create expected_result.
        expected_result = None  # reload() has no return value.

        # Check Cluster optional config values before.
        self.assertEqual(cluster.serve_nodes, _DEFAULT_SERVE_NODES)
        self.assertEqual(cluster.display_name, cluster_id)

        # Perform the method and check the result.
        result = cluster.reload()
        self.assertEqual(result, expected_result)
        self.assertEqual(stub.method_calls, [(
            'GetCluster',
            (request_pb, timeout_seconds),
            {},
        )])

        # Check Cluster optional config values before.
        self.assertEqual(cluster.serve_nodes, serve_nodes)
        self.assertEqual(cluster.display_name, display_name)

    def test_create(self):
        from gcloud._testing import _Monkey
        from gcloud.bigtable._generated import (
            bigtable_cluster_data_pb2 as data_pb2)
        from gcloud.bigtable._generated import operations_pb2
        from gcloud.bigtable._testing import _FakeStub
        from gcloud.bigtable import cluster as MUT

        project = 'PROJECT'
        zone = 'zone'
        cluster_id = 'cluster-id'
        timeout_seconds = 578

        client = _Client(project, timeout_seconds=timeout_seconds)
        cluster = self._makeOne(zone, cluster_id, client)

        # Create request_pb. Just a mock since we monkey patch
        # _prepare_create_request
        request_pb = object()

        # Create response_pb
        op_id = 5678
        op_name = ('operations/projects/%s/zones/%s/clusters/%s/'
                   'operations/%d' % (project, zone, cluster_id, op_id))
        current_op = operations_pb2.Operation(name=op_name)
        response_pb = data_pb2.Cluster(current_operation=current_op)

        # Patch the stub used by the API method.
        client._cluster_stub = stub = _FakeStub(response_pb)

        # Create expected_result.
        expected_result = None  # create() has no return value.

        # Perform the method and check the result.
        prep_create_called = []

        def mock_prep_create_req(cluster):
            prep_create_called.append(cluster)
            return request_pb

        with _Monkey(MUT, _prepare_create_request=mock_prep_create_req):
            result = cluster.create()

        self.assertEqual(result, expected_result)
        self.assertEqual(stub.method_calls, [(
            'CreateCluster',
            (request_pb, timeout_seconds),
            {},
        )])
        self.assertEqual(cluster._operation, current_op)
        self.assertEqual(prep_create_called, [cluster])


class Test__get_pb_property_value(unittest2.TestCase):

    def _callFUT(self, message_pb, property_name):
        from gcloud.bigtable.cluster import _get_pb_property_value
        return _get_pb_property_value(message_pb, property_name)

    def test_it(self):
        from gcloud.bigtable._generated import (
            bigtable_cluster_data_pb2 as data_pb2)
        serve_nodes = 119
        cluster_pb = data_pb2.Cluster(serve_nodes=serve_nodes)
        result = self._callFUT(cluster_pb, 'serve_nodes')
        self.assertEqual(result, serve_nodes)

    def test_with_value_unset_on_pb(self):
        from gcloud.bigtable._generated import (
            bigtable_cluster_data_pb2 as data_pb2)
        cluster_pb = data_pb2.Cluster()
        with self.assertRaises(ValueError):
            self._callFUT(cluster_pb, 'serve_nodes')


class Test__prepare_create_request(unittest2.TestCase):

    def _callFUT(self, cluster):
        from gcloud.bigtable.cluster import _prepare_create_request
        return _prepare_create_request(cluster)

    def test_it(self):
        from gcloud.bigtable._generated import (
            bigtable_cluster_data_pb2 as data_pb2)
        from gcloud.bigtable._generated import (
            bigtable_cluster_service_messages_pb2 as messages_pb2)
        from gcloud.bigtable.cluster import Cluster

        project = 'PROJECT'
        zone = 'zone'
        cluster_id = 'cluster-id'
        display_name = u'DISPLAY_NAME'
        serve_nodes = 8
        client = _Client(project)

        cluster = Cluster(zone, cluster_id, client,
                          display_name=display_name, serve_nodes=serve_nodes)
        request_pb = self._callFUT(cluster)
        self.assertTrue(isinstance(request_pb,
                                   messages_pb2.CreateClusterRequest))
        self.assertEqual(request_pb.cluster_id, cluster_id)
        self.assertEqual(request_pb.name,
                         'projects/' + project + '/zones/' + zone)
        self.assertTrue(isinstance(request_pb.cluster, data_pb2.Cluster))
        self.assertEqual(request_pb.cluster.display_name, display_name)
        self.assertEqual(request_pb.cluster.serve_nodes, serve_nodes)


class _Client(object):

    def __init__(self, project, timeout_seconds=None):
        self.project = project
        self.project_name = 'projects/' + self.project
        self.timeout_seconds = timeout_seconds
