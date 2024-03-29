# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chord.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x63hord.proto\"/\n\x08Response\x12\x12\n\nis_success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"#\n\x07\x41\x64\x64ress\x12\n\n\x02ip\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x05\"3\n\x14NodeRegisterResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x17\n\tIdMessage\x12\n\n\x02id\x18\x01 \x01(\x05\"8\n\x0f\x46ingerTableItem\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x19\n\x07\x61\x64\x64ress\x18\x02 \x01(\x0b\x32\x08.Address\"\x7f\n\x1bPopulateFingerTableResponse\x12\x1b\n\x08response\x18\x01 \x01(\x0b\x32\t.Response\x12%\n\x0bpredecessor\x18\x02 \x01(\x0b\x32\x10.FingerTableItem\x12\x1c\n\x02\x66t\x18\x03 \x03(\x0b\x32\x10.FingerTableItem\"\x1b\n\x0bTextMessage\x12\x0c\n\x04text\x18\x01 \x01(\t\"&\n\tDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\x0c\n\x04text\x18\x02 \x01(\t\".\n\x11\x44\x61taTransferEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"O\n\x0fGetInfoResponse\x12\x1b\n\x08response\x18\x01 \x01(\x0b\x32\t.Response\x12\x1f\n\x05nodes\x18\x02 \x03(\x0b\x32\x10.FingerTableItem\"I\n\x10PassDataResponse\x12\x1b\n\x08response\x18\x01 \x01(\x0b\x32\t.Response\x12\x18\n\x04\x64\x61ta\x18\x02 \x03(\x0b\x32\n.DataEntry\"Q\n\x0eInheritRequest\x12%\n\x0bpredecessor\x18\x01 \x01(\x0b\x32\x10.FingerTableItem\x12\x18\n\x04\x64\x61ta\x18\x02 \x03(\x0b\x32\n.DataEntry2x\n\x0b\x43RUDService\x12%\n\x04save\x12\x12.DataTransferEntry\x1a\t.Response\x12!\n\x06remove\x12\x0c.TextMessage\x1a\t.Response\x12\x1f\n\x04\x66ind\x12\x0c.TextMessage\x1a\t.Response2e\n\x13\x43lientServerService\x12\"\n\x07\x63onnect\x12\x0c.TextMessage\x1a\t.Response\x12*\n\x08get_info\x12\x0c.TextMessage\x1a\x10.GetInfoResponse2\xba\x01\n\x0fNodeNodeService\x12%\n\x07inherit\x12\x0f.InheritRequest\x1a\t.Response\x12\x30\n\tpass_data\x12\x10.FingerTableItem\x1a\x11.PassDataResponse\x12/\n\x10update_successor\x12\x10.FingerTableItem\x1a\t.Response\x12\x1d\n\x04save\x12\n.DataEntry\x1a\t.Response2\xaa\x01\n\x13NodeRegistryService\x12+\n\x08register\x12\x08.Address\x1a\x15.NodeRegisterResponse\x12#\n\nderegister\x12\n.IdMessage\x1a\t.Response\x12\x41\n\x15populate_finger_table\x12\n.IdMessage\x1a\x1c.PopulateFingerTableResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chord_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _RESPONSE._serialized_start=15
  _RESPONSE._serialized_end=62
  _ADDRESS._serialized_start=64
  _ADDRESS._serialized_end=99
  _NODEREGISTERRESPONSE._serialized_start=101
  _NODEREGISTERRESPONSE._serialized_end=152
  _IDMESSAGE._serialized_start=154
  _IDMESSAGE._serialized_end=177
  _FINGERTABLEITEM._serialized_start=179
  _FINGERTABLEITEM._serialized_end=235
  _POPULATEFINGERTABLERESPONSE._serialized_start=237
  _POPULATEFINGERTABLERESPONSE._serialized_end=364
  _TEXTMESSAGE._serialized_start=366
  _TEXTMESSAGE._serialized_end=393
  _DATAENTRY._serialized_start=395
  _DATAENTRY._serialized_end=433
  _DATATRANSFERENTRY._serialized_start=435
  _DATATRANSFERENTRY._serialized_end=481
  _GETINFORESPONSE._serialized_start=483
  _GETINFORESPONSE._serialized_end=562
  _PASSDATARESPONSE._serialized_start=564
  _PASSDATARESPONSE._serialized_end=637
  _INHERITREQUEST._serialized_start=639
  _INHERITREQUEST._serialized_end=720
  _CRUDSERVICE._serialized_start=722
  _CRUDSERVICE._serialized_end=842
  _CLIENTSERVERSERVICE._serialized_start=844
  _CLIENTSERVERSERVICE._serialized_end=945
  _NODENODESERVICE._serialized_start=948
  _NODENODESERVICE._serialized_end=1134
  _NODEREGISTRYSERVICE._serialized_start=1137
  _NODEREGISTRYSERVICE._serialized_end=1307
# @@protoc_insertion_point(module_scope)
