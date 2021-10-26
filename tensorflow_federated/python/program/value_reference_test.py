# Copyright 2021, The TensorFlow Federated Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Union

from absl.testing import absltest
from absl.testing import parameterized
import attr
import numpy as np
import tensorflow as tf

from tensorflow_federated.python.program import value_reference


@attr.s
class _TestAttrObject():
  a = attr.ib()
  b = attr.ib()


class _TestServerArrayReference(value_reference.ServerArrayReference):

  def __init__(self, value: Union[np.generic, np.ndarray]):
    self._value = value

  @property
  def type_signature(self):
    return None

  def get_value(self) -> Union[np.generic, np.ndarray]:
    return self._value


class MaterializeValueTest(parameterized.TestCase, tf.test.TestCase):

  # pyformat: disable
  @parameterized.named_parameters(
      ('none', None, None),
      ('bool', True, True),
      ('int', 1, 1),
      ('str', 'a', 'a'),
      ('list', [True, 1, 'a'], [True, 1, 'a']),
      ('list_empty', [], []),
      ('list_nested', [[True, 1, 'a'], [False]], [[True, 1, 'a'], [False]]),
      ('dict', {'a': True, 'b': 1, 'c': 'a'}, {'a': True, 'b': 1, 'c': 'a'}),
      ('dict_empty', {}, {}),
      ('dict_nested',
       {'x': {'a': True, 'b': 1, 'c': 'a'}, 'y': {'a': False}},
       {'x': {'a': True, 'b': 1, 'c': 'a'}, 'y': {'a': False}}),
      ('tensor_int', tf.constant(1), tf.constant(1)),
      ('tensor_str', tf.constant('a'), tf.constant('a')),
      ('tensor_2d', tf.ones((2, 3)), tf.ones((2, 3))),
      ('tensor_nested',
       {'a': [tf.constant(1)], 'b': tf.constant(2)},
       {'a': [tf.constant(1)], 'b': tf.constant(2)}),
      ('numpy_int', np.int32(1), np.int32(1)),
      ('numpy_2d', np.ones((2, 3)), np.ones((2, 3))),
      ('numpy_nested',
       {'a': [np.int32(1)], 'b': np.int32(2)},
       {'a': [np.int32(1)], 'b': np.int32(2)}),
      ('attr', _TestAttrObject(1, 2), _TestAttrObject(1, 2)),
      ('attr_nested',
       {'a': [_TestAttrObject(1, 2)], 'b': _TestAttrObject(3, 4)},
       {'a': [_TestAttrObject(1, 2)], 'b': _TestAttrObject(3, 4)}),
      ('server_array_reference', _TestServerArrayReference(1), 1),
      ('server_array_reference_nested',
       {'a': [_TestServerArrayReference(1)], 'b': _TestServerArrayReference(2)},
       {'a': [1], 'b': 2}),
      ('materialized_values_and_value_references',
       [1, _TestServerArrayReference(2)],
       [1, 2]),
  )
  # pyformat: enable
  def test_returns_value(self, value, expected_value):
    actual_value = value_reference.materialize_value(value)

    if ((isinstance(actual_value, tf.Tensor) and
         isinstance(expected_value, tf.Tensor)) or
        (isinstance(actual_value, np.ndarray) and
         isinstance(expected_value, np.ndarray))):
      self.assertAllEqual(actual_value, expected_value)
    else:
      self.assertEqual(actual_value, expected_value)


if __name__ == '__main__':
  absltest.main()
