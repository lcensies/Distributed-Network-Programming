# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chord_pb2 as chord__pb2


class CRUDServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.save = channel.unary_unary(
                '/CRUDService/save',
                request_serializer=chord__pb2.DataTransferEntry.SerializeToString,
                response_deserializer=chord__pb2.Response.FromString,
                )
        self.remove = channel.unary_unary(
                '/CRUDService/remove',
                request_serializer=chord__pb2.TextMessage.SerializeToString,
                response_deserializer=chord__pb2.Response.FromString,
                )
        self.find = channel.unary_unary(
                '/CRUDService/find',
                request_serializer=chord__pb2.TextMessage.SerializeToString,
                response_deserializer=chord__pb2.Response.FromString,
                )


class CRUDServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def save(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def remove(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def find(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CRUDServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'save': grpc.unary_unary_rpc_method_handler(
                    servicer.save,
                    request_deserializer=chord__pb2.DataTransferEntry.FromString,
                    response_serializer=chord__pb2.Response.SerializeToString,
            ),
            'remove': grpc.unary_unary_rpc_method_handler(
                    servicer.remove,
                    request_deserializer=chord__pb2.TextMessage.FromString,
                    response_serializer=chord__pb2.Response.SerializeToString,
            ),
            'find': grpc.unary_unary_rpc_method_handler(
                    servicer.find,
                    request_deserializer=chord__pb2.TextMessage.FromString,
                    response_serializer=chord__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'CRUDService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class CRUDService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def save(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/CRUDService/save',
            chord__pb2.DataTransferEntry.SerializeToString,
            chord__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def remove(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/CRUDService/remove',
            chord__pb2.TextMessage.SerializeToString,
            chord__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def find(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/CRUDService/find',
            chord__pb2.TextMessage.SerializeToString,
            chord__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class ClientServerServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.connect = channel.unary_unary(
                '/ClientServerService/connect',
                request_serializer=chord__pb2.TextMessage.SerializeToString,
                response_deserializer=chord__pb2.Response.FromString,
                )
        self.get_info = channel.unary_unary(
                '/ClientServerService/get_info',
                request_serializer=chord__pb2.TextMessage.SerializeToString,
                response_deserializer=chord__pb2.GetInfoResponse.FromString,
                )


class ClientServerServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def connect(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_info(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ClientServerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'connect': grpc.unary_unary_rpc_method_handler(
                    servicer.connect,
                    request_deserializer=chord__pb2.TextMessage.FromString,
                    response_serializer=chord__pb2.Response.SerializeToString,
            ),
            'get_info': grpc.unary_unary_rpc_method_handler(
                    servicer.get_info,
                    request_deserializer=chord__pb2.TextMessage.FromString,
                    response_serializer=chord__pb2.GetInfoResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ClientServerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ClientServerService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def connect(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientServerService/connect',
            chord__pb2.TextMessage.SerializeToString,
            chord__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def get_info(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientServerService/get_info',
            chord__pb2.TextMessage.SerializeToString,
            chord__pb2.GetInfoResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class NodeNodeServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.inherit = channel.unary_unary(
                '/NodeNodeService/inherit',
                request_serializer=chord__pb2.InheritRequest.SerializeToString,
                response_deserializer=chord__pb2.Response.FromString,
                )
        self.pass_data = channel.unary_unary(
                '/NodeNodeService/pass_data',
                request_serializer=chord__pb2.FingerTableItem.SerializeToString,
                response_deserializer=chord__pb2.PassDataResponse.FromString,
                )
        self.update_successor = channel.unary_unary(
                '/NodeNodeService/update_successor',
                request_serializer=chord__pb2.FingerTableItem.SerializeToString,
                response_deserializer=chord__pb2.Response.FromString,
                )
        self.save = channel.unary_unary(
                '/NodeNodeService/save',
                request_serializer=chord__pb2.DataEntry.SerializeToString,
                response_deserializer=chord__pb2.Response.FromString,
                )


class NodeNodeServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def inherit(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def pass_data(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def update_successor(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def save(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NodeNodeServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'inherit': grpc.unary_unary_rpc_method_handler(
                    servicer.inherit,
                    request_deserializer=chord__pb2.InheritRequest.FromString,
                    response_serializer=chord__pb2.Response.SerializeToString,
            ),
            'pass_data': grpc.unary_unary_rpc_method_handler(
                    servicer.pass_data,
                    request_deserializer=chord__pb2.FingerTableItem.FromString,
                    response_serializer=chord__pb2.PassDataResponse.SerializeToString,
            ),
            'update_successor': grpc.unary_unary_rpc_method_handler(
                    servicer.update_successor,
                    request_deserializer=chord__pb2.FingerTableItem.FromString,
                    response_serializer=chord__pb2.Response.SerializeToString,
            ),
            'save': grpc.unary_unary_rpc_method_handler(
                    servicer.save,
                    request_deserializer=chord__pb2.DataEntry.FromString,
                    response_serializer=chord__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'NodeNodeService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NodeNodeService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def inherit(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NodeNodeService/inherit',
            chord__pb2.InheritRequest.SerializeToString,
            chord__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def pass_data(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NodeNodeService/pass_data',
            chord__pb2.FingerTableItem.SerializeToString,
            chord__pb2.PassDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def update_successor(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NodeNodeService/update_successor',
            chord__pb2.FingerTableItem.SerializeToString,
            chord__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def save(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NodeNodeService/save',
            chord__pb2.DataEntry.SerializeToString,
            chord__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class NodeRegistryServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.register = channel.unary_unary(
                '/NodeRegistryService/register',
                request_serializer=chord__pb2.Address.SerializeToString,
                response_deserializer=chord__pb2.NodeRegisterResponse.FromString,
                )
        self.deregister = channel.unary_unary(
                '/NodeRegistryService/deregister',
                request_serializer=chord__pb2.IdMessage.SerializeToString,
                response_deserializer=chord__pb2.Response.FromString,
                )
        self.populate_finger_table = channel.unary_unary(
                '/NodeRegistryService/populate_finger_table',
                request_serializer=chord__pb2.IdMessage.SerializeToString,
                response_deserializer=chord__pb2.PopulateFingerTableResponse.FromString,
                )


class NodeRegistryServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def deregister(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def populate_finger_table(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NodeRegistryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'register': grpc.unary_unary_rpc_method_handler(
                    servicer.register,
                    request_deserializer=chord__pb2.Address.FromString,
                    response_serializer=chord__pb2.NodeRegisterResponse.SerializeToString,
            ),
            'deregister': grpc.unary_unary_rpc_method_handler(
                    servicer.deregister,
                    request_deserializer=chord__pb2.IdMessage.FromString,
                    response_serializer=chord__pb2.Response.SerializeToString,
            ),
            'populate_finger_table': grpc.unary_unary_rpc_method_handler(
                    servicer.populate_finger_table,
                    request_deserializer=chord__pb2.IdMessage.FromString,
                    response_serializer=chord__pb2.PopulateFingerTableResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'NodeRegistryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NodeRegistryService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NodeRegistryService/register',
            chord__pb2.Address.SerializeToString,
            chord__pb2.NodeRegisterResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def deregister(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NodeRegistryService/deregister',
            chord__pb2.IdMessage.SerializeToString,
            chord__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def populate_finger_table(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NodeRegistryService/populate_finger_table',
            chord__pb2.IdMessage.SerializeToString,
            chord__pb2.PopulateFingerTableResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)