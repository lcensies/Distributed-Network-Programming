# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\"\x1e\n\x0bTextMessage\x12\x0f\n\x07message\x18\x01 \x01(\t\"2\n\x10SplitTextRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\r\n\x05\x64\x65lim\x18\x02 \x01(\t\"\x1d\n\x0eIntegerMessage\x12\x0b\n\x03num\x18\x01 \x01(\x03\"-\n\x1aReverseTextMessageResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\":\n\x18SplitTextMessageResponse\x12\x0f\n\x07n_parts\x18\x01 \x01(\x05\x12\r\n\x05parts\x18\x02 \x03(\t2\xb7\x01\n\x07Service\x12\x38\n\x0bReverseText\x12\x0c.TextMessage\x1a\x1b.ReverseTextMessageResponse\x12\x39\n\tSplitText\x12\x11.SplitTextRequest\x1a\x19.SplitTextMessageResponse\x12\x37\n\x10GetIsPrimeStream\x12\x0f.IntegerMessage\x1a\x0c.TextMessage\"\x00(\x01\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _TEXTMESSAGE._serialized_start=17
  _TEXTMESSAGE._serialized_end=47
  _SPLITTEXTREQUEST._serialized_start=49
  _SPLITTEXTREQUEST._serialized_end=99
  _INTEGERMESSAGE._serialized_start=101
  _INTEGERMESSAGE._serialized_end=130
  _REVERSETEXTMESSAGERESPONSE._serialized_start=132
  _REVERSETEXTMESSAGERESPONSE._serialized_end=177
  _SPLITTEXTMESSAGERESPONSE._serialized_start=179
  _SPLITTEXTMESSAGERESPONSE._serialized_end=237
  _SERVICE._serialized_start=240
  _SERVICE._serialized_end=423
# @@protoc_insertion_point(module_scope)