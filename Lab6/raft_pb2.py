# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\"\x1b\n\x0bTextMessage\x12\x0c\n\x04text\x18\x01 \x01(\t\"*\n\x0bRaftAddress\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\"+\n\x0bRaftRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0e\n\x06nodeId\x18\x02 \x01(\x05\"-\n\x0cRaftResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07success\x18\x02 \x01(\x08\x32\xb6\x01\n\nRaftServer\x12,\n\rAppendEntries\x12\x0c.RaftRequest\x1a\r.RaftResponse\x12\'\n\tGetLeader\x12\x0c.TextMessage\x1a\x0c.RaftAddress\x12%\n\x07Suspend\x12\x0c.TextMessage\x1a\x0c.TextMessage\x12*\n\x0bRequestVote\x12\x0c.RaftRequest\x1a\r.RaftResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _TEXTMESSAGE._serialized_start=14
  _TEXTMESSAGE._serialized_end=41
  _RAFTADDRESS._serialized_start=43
  _RAFTADDRESS._serialized_end=85
  _RAFTREQUEST._serialized_start=87
  _RAFTREQUEST._serialized_end=130
  _RAFTRESPONSE._serialized_start=132
  _RAFTRESPONSE._serialized_end=177
  _RAFTSERVER._serialized_start=180
  _RAFTSERVER._serialized_end=362
# @@protoc_insertion_point(module_scope)
