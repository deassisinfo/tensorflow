# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Tests for XLA JIT compiler."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin

from tensorflow.compiler.tests.xla_test import XLATestCase
from tensorflow.python.framework import dtypes
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import gen_nn_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import nn_ops
from tensorflow.python.platform import googletest


class UnaryOpsTest(XLATestCase):
  """Test cases for unary operators."""

  def _assertOpOutputMatchesExpected(self, op, inp, expected,
                                     equality_test=None, rtol=1e-3, atol=1e-5):
    """Verifies that 'op' produces 'expected' when fed input 'inp' .

    Args:
      op: operator to test
      inp: numpy input array to use as input to 'op'.
      expected: numpy array representing the expected output of 'op'.
      equality_test: either None, or a function that tests two numpy arrays for
        equality. If None, self.assertAllClose is used.
      rtol: relative tolerance for equality test.
      atol: absolute tolerance for equality test.
    """
    with self.test_session() as session:
      with self.test_scope():
        pinp = array_ops.placeholder(
            dtypes.as_dtype(inp.dtype), inp.shape, name="a")
        output = op(pinp)
      result = session.run(output, {pinp: inp})
      if equality_test is None:
        equality_test = self.assertAllClose
      equality_test(result, expected, rtol=rtol, atol=atol)

  def ListsAreClose(self, result, expected, rtol, atol):
    """Tests closeness of two lists of floats."""
    self.assertEqual(len(result), len(expected))
    for i in xrange(len(result)):
      self.assertAllClose(result[i], expected[i], rtol, atol)

  def testAllTypeOps(self):
    for dtype in self.numeric_types:
      self._assertOpOutputMatchesExpected(
          array_ops.diag,
          np.array([1, 2, 3, 4], dtype=dtype),
          np.array([[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 3, 0], [0, 0, 0, 4]],
                   dtype=dtype))
      self._assertOpOutputMatchesExpected(
          array_ops.diag_part,
          np.arange(36).reshape([2, 3, 2, 3]).astype(dtype),
          np.array([[0, 7, 14], [21, 28, 35]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          array_ops.identity,
          np.array([[-1, 1]], dtype=dtype),
          expected=np.array([[-1, 1]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          array_ops.matrix_diag,
          np.array([[1, 2], [3, 4]], dtype=dtype),
          np.array([[[1, 0], [0, 2]], [[3, 0], [0, 4]]], dtype=dtype))
      self._assertOpOutputMatchesExpected(
          array_ops.matrix_diag_part,
          np.arange(3 * 2 * 4).reshape([3, 2, 4]).astype(dtype),
          np.array([[0, 5], [8, 13], [16, 21]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          array_ops.prevent_gradient,
          np.array([[-1, 1]], dtype=dtype),
          expected=np.array([[-1, 1]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          array_ops.squeeze,
          np.array([[[[[]]]]], dtype=dtype),
          expected=np.array([], dtype=dtype))
      self._assertOpOutputMatchesExpected(
          array_ops.squeeze,
          np.array([[[1], [2]]], dtype=dtype),
          expected=np.array([1, 2], dtype=dtype))
      self._assertOpOutputMatchesExpected(
          array_ops.squeeze,
          np.array([[[1]], [[2]]], dtype=dtype),
          expected=np.array([1, 2], dtype=dtype))
      self._assertOpOutputMatchesExpected(
          array_ops.squeeze,
          np.array([[[1, 2], [3, 4]]], dtype=dtype),
          expected=np.array([[1, 2], [3, 4]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          array_ops.stop_gradient,
          np.array([[-1, 1]], dtype=dtype),
          expected=np.array([[-1, 1]], dtype=dtype))

  def testFloatOps(self):
    for dtype in self.float_types:
      self._assertOpOutputMatchesExpected(
          math_ops.acosh,
          np.array([1, 2, 3, 4], dtype=dtype),
          expected=np.array([0, 1.3169579, 1.76274717, 2.06343707],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.asinh,
          np.array([1, 2, 3, 4], dtype=dtype),
          expected=np.array([0.88137359, 1.44363548, 1.81844646, 2.09471255],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.atanh,
          np.array([0.1, 0.2, 0.3, 0.4], dtype=dtype),
          expected=np.array([0.10033535, 0.20273255, 0.3095196, 0.42364893],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.ceil,
          np.array([[-1.7, 1.2]], dtype=dtype),
          expected=np.array([[-1, 2]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.cosh,
          np.array([1, 2, 3, 4], dtype=dtype),
          expected=np.array([1.54308063, 3.76219569, 10.067662, 27.30823284],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.exp,
          np.array([[-1, 1]], dtype=dtype),
          expected=np.array([[0.36787945, 2.7182817]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.expm1,
          np.array([[-1, 1]], dtype=dtype),
          expected=np.array([[-0.63212056, 1.71828183]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.floor,
          np.array([[-1.7, 1.2]], dtype=dtype),
          expected=np.array([[-2, 1]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.is_finite,
          np.array([[np.NINF, -2, -1, 0, 0.5, 1, 2, np.inf, np.nan]],
                   dtype=dtype),
          expected=np.array([[0, 1, 1, 1, 1, 1, 1, 0, 0]], dtype=np.bool))

      # Tests for tf.nn ops.
      self._assertOpOutputMatchesExpected(
          nn_ops.l2_loss, np.array([[[]]], dtype=dtype), expected=dtype(0))

      self._assertOpOutputMatchesExpected(nn_ops.l2_loss, dtype(4), dtype(8))

      self._assertOpOutputMatchesExpected(
          nn_ops.l2_loss, np.array([[-2, 4]], dtype=dtype), expected=dtype(10))

      self._assertOpOutputMatchesExpected(
          math_ops.reciprocal,
          np.array([[1, 2]], dtype=dtype),
          expected=np.array([[1, 0.5]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.log,
          np.array([[1, 2]], dtype=dtype),
          expected=np.array([[0, 0.69314718]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.sin,
          np.array([[1, 2]], dtype=dtype),
          expected=np.array([[0.841478, 0.909302]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.cos,
          np.array([[1, 2]], dtype=dtype),
          expected=np.array([[0.540297, -0.41614]], dtype=dtype))

      # TODO(b/34703906): improve log1p implementation and make tolerance
      # tighter.
      self._assertOpOutputMatchesExpected(
          math_ops.log1p,
          np.array([[1e-14, 1e-15, 0.6]], dtype=dtype),
          expected=np.log1p(np.array([[1e-14, 1e-15, 0.6]], dtype=dtype)))

      self._assertOpOutputMatchesExpected(
          math_ops.rint,
          np.array([[-1.7, 1.2, 4.0, 0.0], [-3.5, -2.5, -1.5, -0.5],
                    [0.5, 1.5, 2.5, 3.5]], dtype=dtype),
          expected=np.array([[-2, 1, 4, 0], [-4, -2, -2, 0], [0, 2, 2, 4]],
                            dtype=dtype))
      self._assertOpOutputMatchesExpected(
          math_ops.round,
          np.array([[-1.7, 1.2, 4.0, 0.0], [-3.5, -2.5, -1.5, -0.5],
                    [0.5, 1.5, 2.5, 3.5]], dtype=dtype),
          expected=np.array([[-2, 1, 4, 0], [-4, -2, -2, 0], [0, 2, 2, 4]],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.rsqrt,
          np.array([[4, 16]], dtype=dtype),
          expected=np.array([[0.5, 0.25]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.sigmoid,
          np.array(
              [[1, 1, 1, 1],
               [1, 2, 3, 4]],
              dtype=dtype),
          expected=np.array(
              [[0.7310586, 0.7310586, 0.7310586, 0.7310586],
               [0.7310586, 0.880797, 0.95257413, 0.98201376]],
              dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.sigmoid,
          np.array([-300, -150, 0, 150, 300], dtype=dtype),
          expected=np.array([0, 0, 0.5, 1, 1], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.sinh,
          np.array([1, 2, 3, 4], dtype=dtype),
          expected=np.array([1.17520119, 3.62686041, 10.01787493, 27.2899172],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.sqrt,
          np.array([[4, 9]], dtype=dtype),
          expected=np.array([[2, 3]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.tan,
          np.array([1, 2, 3, 4], dtype=dtype),
          expected=np.array([1.55740772, -2.18503986, -0.14254654, 1.15782128],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.tanh,
          np.array(
              [[1, 1, 1, 1],
               [1, 2, 3, 4]],
              dtype=dtype),
          expected=np.array(
              [[0.76159418, 0.76159418, 0.76159418, 0.76159418],
               [0.76159418, 0.96402758, 0.99505478, 0.99932933]],
              dtype=dtype))

      self._assertOpOutputMatchesExpected(
          nn_ops.log_softmax,
          np.array(
              [[1, 1, 1, 1],
               [1, 2, 3, 4]],
              dtype=dtype),
          expected=np.array(
              [[-1.3862944, -1.3862944, -1.3862944, -1.3862944],
               [-3.4401896, -2.4401896, -1.4401897, -0.44018969]],
              dtype=dtype))

      self._assertOpOutputMatchesExpected(
          nn_ops.elu,
          np.array([[-1, 0, 1]], dtype=dtype),
          expected=np.array([[-0.63212056, 0, 1]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          nn_ops.selu,
          np.array([[-1, 0, 1]], dtype=dtype),
          expected=np.array([[-1.11133074, 0., 1.05070099]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          nn_ops.relu,
          np.array([[-1, 1]], dtype=dtype),
          expected=np.array([[0, 1]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          nn_ops.relu6,
          np.array([[-0.05, 6.05, 5]], dtype=dtype),
          expected=np.array([[0, 6, 5]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          nn_ops.softmax,
          np.array(
              [[1, 1, 1, 1],
               [1, 2, 3, 4]],
              dtype=dtype),
          expected=np.array(
              [[0.25, 0.25, 0.25, 0.25],
               [0.032058604, 0.087144323, 0.23688284, 0.64391428]],
              dtype=dtype))

      self._assertOpOutputMatchesExpected(
          nn_ops.softsign,
          np.array([[-2, -1, 0, 1, 2]], dtype=dtype),
          expected=np.array([[-0.66666669, -0.5, 0, 0.5, 0.66666669]],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.is_finite,
          np.array(
              [[42, float("inf"), -123], [float("nan"), 0, -0.0]], dtype=dtype),
          expected=np.array(
              [[True, False, True], [False, True, True]], dtype=np.bool))

      self._assertOpOutputMatchesExpected(
          lambda x: array_ops.quantize_and_dequantize_v2(x, -127, 127, True, 8),
          np.array([-1, -0.5, 0, 0.3], dtype=dtype),
          expected=np.array([-1, -64.0 / 127, 0, 38.0 / 127], dtype=dtype))

  def testNumericOps(self):
    for dtype in self.numeric_types:
      self._assertOpOutputMatchesExpected(
          math_ops.abs,
          np.array([[2, -1]], dtype=dtype),
          expected=np.array([[2, 1]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.negative,
          np.array([[-1, 1]], dtype=dtype),
          expected=np.array([[1, -1]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          math_ops.square,
          np.array([[-2, 3]], dtype=dtype),
          expected=np.array([[4, 9]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          array_ops.zeros_like,
          np.array([[4, 3], [2, 1]], dtype=dtype),
          expected=np.array([[0, 0], [0, 0]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          array_ops.ones_like,
          np.array([[4, 3], [2, 1]], dtype=dtype),
          expected=np.array([[1, 1], [1, 1]], dtype=dtype))

  # TODO(phawkins): these tests fail unless fastmath optimizations
  # are disabled. Use more robust IsInf/IsNaN detection and enable these
  # tests.
  @unittest.skip("test case fails in fast-math mode")
  def testIsInfAndIsNan(self):
    for dtype in self.float_types:
      self._assertOpOutputMatchesExpected(
          math_ops.is_inf,
          np.array([[np.NINF, -2, -1, 0, 0.5, 1, 2, np.inf, np.nan]],
                   dtype=dtype),
          expected=np.array([[1, 0, 0, 0, 0, 0, 0, 1, 0]], dtype=np.bool))
      self._assertOpOutputMatchesExpected(
          math_ops.is_nan,
          np.array([[np.NINF, -2, -1, 0, 0.5, 1, 2, np.inf, np.nan]],
                   dtype=dtype),
          expected=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=np.bool))

  def testLogicalOps(self):
    self._assertOpOutputMatchesExpected(
        math_ops.logical_not,
        np.array([[True, False], [False, True]], dtype=np.bool),
        expected=np.array([[False, True], [True, False]], dtype=np.bool))

  def testBiasAddGrad(self):
    self._assertOpOutputMatchesExpected(
        gen_nn_ops.bias_add_grad,
        np.array([[1., 2.], [3., 4.]], dtype=np.float32),
        expected=np.array([4., 6.], dtype=np.float32))

    self._assertOpOutputMatchesExpected(
        lambda x: gen_nn_ops.bias_add_grad(x, data_format="NCHW"),
        np.array([[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]],
                 dtype=np.float32),
        expected=np.array([10., 26.], dtype=np.float32))

  def testCast(self):
    shapes = [[], [4], [2, 3], [2, 0, 4]]
    types = [dtypes.bool, dtypes.int32, dtypes.float32]
    for shape in shapes:
      for src_type in types:
        for dst_type in types:
          src = np.arange(np.prod(shape)).astype(src_type.as_numpy_dtype)
          src = src.reshape(shape)

          dst = src.astype(dst_type.as_numpy_dtype)
          self._assertOpOutputMatchesExpected(
              lambda x, dst_type=dst_type: math_ops.cast(x, dst_type),
              src,
              expected=dst)

  def testInvertPermutation(self):
    self._assertOpOutputMatchesExpected(
        array_ops.invert_permutation,
        np.array([1, 2, 0], np.int32),
        expected=np.array([2, 0, 1], dtype=np.int32))

  def testRank(self):
    rank_op = lambda x: array_ops.rank_internal(x, optimize=False)
    for dtype in self.numeric_types:
      self._assertOpOutputMatchesExpected(
          rank_op, dtype(7), expected=np.int32(0))
      self._assertOpOutputMatchesExpected(
          rank_op, np.array(
              [[], []], dtype=dtype), expected=np.int32(2))
      self._assertOpOutputMatchesExpected(
          rank_op, np.array(
              [-1, 1], dtype=dtype), expected=np.int32(1))
      self._assertOpOutputMatchesExpected(
          rank_op, np.array(
              [[-1, 1]], dtype=dtype), expected=np.int32(2))
      self._assertOpOutputMatchesExpected(
          rank_op,
          np.array([[-1], [1], [4]], dtype=dtype),
          expected=np.int32(2))

  def testShape(self):
    shape_op = lambda x: array_ops.shape_internal(x, optimize=False)
    for dtype in self.numeric_types:
      self._assertOpOutputMatchesExpected(
          shape_op, dtype(7), expected=np.array([], dtype=np.int32))
      self._assertOpOutputMatchesExpected(
          shape_op,
          np.array([[], []], dtype=dtype),
          expected=np.array([2, 0], dtype=np.int32))
      self._assertOpOutputMatchesExpected(
          shape_op,
          np.array([-1, 1], dtype=dtype),
          expected=np.array([2], dtype=np.int32))
      self._assertOpOutputMatchesExpected(
          shape_op,
          np.array([[-1, 1]], dtype=dtype),
          expected=np.array([1, 2], dtype=np.int32))
      self._assertOpOutputMatchesExpected(
          shape_op,
          np.array([[-1], [1], [4]], dtype=dtype),
          expected=np.array([3, 1], dtype=np.int32))

  def testSize(self):
    size_op = lambda x: array_ops.size_internal(x, optimize=False)
    for dtype in self.numeric_types:
      self._assertOpOutputMatchesExpected(
          size_op, dtype(7), expected=np.int32(1))
      self._assertOpOutputMatchesExpected(
          size_op, np.array([[], []], dtype=dtype), expected=np.int32(0))
      self._assertOpOutputMatchesExpected(
          size_op, np.array([-1, 1], dtype=dtype), expected=np.int32(2))
      self._assertOpOutputMatchesExpected(
          size_op, np.array([[-1, 1]], dtype=dtype), expected=np.int32(2))
      self._assertOpOutputMatchesExpected(
          size_op,
          np.array([[-1], [1], [4]], dtype=dtype),
          expected=np.int32(3))

  def testUnpack(self):
    self._assertOpOutputMatchesExpected(
        array_ops.unstack,
        np.array([[1., 2.], [3., 4.], [5., 6.]], dtype=np.float32),
        expected=[
            np.array([1., 2.], dtype=np.float32),
            np.array([3., 4.], dtype=np.float32),
            np.array([5., 6.], dtype=np.float32),
        ],
        equality_test=self.ListsAreClose)

    self._assertOpOutputMatchesExpected(
        lambda x: array_ops.unstack(x, axis=1),
        np.array([[1., 2.], [3., 4.], [5., 6.]], dtype=np.float32),
        expected=[
            np.array([1., 3., 5.], dtype=np.float32),
            np.array([2., 4., 6.], dtype=np.float32),
        ],
        equality_test=self.ListsAreClose)

  def testDepthToSpace(self):
    for dtype in self.numeric_types:
      self._assertOpOutputMatchesExpected(
          lambda x: array_ops.depth_to_space(x, block_size=2),
          np.array([[[[1, 2, 3, 4]]]], dtype=dtype),
          expected=np.array([[[[1], [2]],
                              [[3], [4]]]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          lambda x: array_ops.depth_to_space(x, block_size=2),
          np.array([[[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]]], dtype=dtype),
          expected=np.array([[[[1, 2, 3], [4, 5, 6]],
                              [[7, 8, 9], [10, 11, 12]]]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          lambda x: array_ops.depth_to_space(x, block_size=2),
          np.array([[[[1, 2, 3, 4],
                      [5, 6, 7, 8]],
                     [[9, 10, 11, 12],
                      [13, 14, 15, 16]]]], dtype=dtype),
          expected=np.array([[[[1], [2], [5], [6]],
                              [[3], [4], [7], [8]],
                              [[9], [10], [13], [14]],
                              [[11], [12], [15], [16]]]], dtype=dtype))

  def testSpaceToDepth(self):
    for dtype in self.numeric_types:
      self._assertOpOutputMatchesExpected(
          lambda x: array_ops.space_to_depth(x, block_size=2),
          np.array([[[[1], [2]],
                     [[3], [4]]]], dtype=dtype),
          expected=np.array([[[[1, 2, 3, 4]]]], dtype=dtype))

      self._assertOpOutputMatchesExpected(
          lambda x: array_ops.space_to_depth(x, block_size=2),
          np.array([[[[1, 2, 3], [4, 5, 6]],
                     [[7, 8, 9], [10, 11, 12]]]], dtype=dtype),
          expected=np.array([[[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]]],
                            dtype=dtype))

      self._assertOpOutputMatchesExpected(
          lambda x: array_ops.space_to_depth(x, block_size=2),
          np.array([[[[1], [2], [5], [6]],
                     [[3], [4], [7], [8]],
                     [[9], [10], [13], [14]],
                     [[11], [12], [15], [16]]]], dtype=dtype),
          expected=np.array([[[[1, 2, 3, 4],
                               [5, 6, 7, 8]],
                              [[9, 10, 11, 12],
                               [13, 14, 15, 16]]]], dtype=dtype))

  def _assertSoftplusMatchesExpected(self, features, dtype):
    features = np.array(features, dtype=dtype)
    zero = np.asarray(0).astype(dtype)
    expected = np.logaddexp(zero, features)
    self._assertOpOutputMatchesExpected(
        nn_ops.softplus, features, expected=expected)

  def testSoftplus(self):
    for dtype in self.float_types:
      self._assertSoftplusMatchesExpected([[-2, 0, 8]], dtype)
      self._assertSoftplusMatchesExpected(
          [[-9, 7, -5, 3, -1], [1, -3, 5, -7, 9]], dtype)
      log_eps = np.log(np.finfo(dtype).eps)
      one = dtype(1)
      ten = dtype(10)
      self._assertSoftplusMatchesExpected([
          log_eps, log_eps - one, log_eps + one, log_eps - ten,
          log_eps + ten, -log_eps, -log_eps - one, -log_eps + one,
          -log_eps - ten, -log_eps + ten], dtype)

if __name__ == "__main__":
  googletest.main()
