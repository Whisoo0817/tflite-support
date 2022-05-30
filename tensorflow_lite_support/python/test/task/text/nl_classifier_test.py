# Copyright 2022 The TensorFlow Authors. All Rights Reserved.
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
"""Tests for nl_classifier."""

import enum

from absl.testing import parameterized

import tensorflow as tf
from tensorflow_lite_support.python.task.core import base_options as base_options_module
from tensorflow_lite_support.python.task.processor.proto import class_pb2
from tensorflow_lite_support.python.task.processor.proto import classifications_pb2
from tensorflow_lite_support.python.task.processor.proto import nl_classification_options_pb2
from tensorflow_lite_support.python.task.text import nl_classifier
from tensorflow_lite_support.python.test import test_util

_BaseOptions = base_options_module.BaseOptions
_NLClassifier = nl_classifier.NLClassifier
_Category = class_pb2.Category
_Classifications = classifications_pb2.Classifications
_ClassificationResult = classifications_pb2.ClassificationResult
_NLClassifierOptions = nl_classifier.NLClassifierOptions
_NLClassificationOptions = nl_classification_options_pb2.NLClassificationOptions


_REGEX_TOKENIZER_MODEL = 'test_model_nl_classifier_with_regex_tokenizer.tflite'
_POSITIVE_INPUT = "This is the best movie I’ve seen in recent years. " \
                  "Strongly recommend it!"
_EXPECTED_RESULTS_OF_POSITIVE_INPUT = _ClassificationResult(
  classifications=[
    _Classifications(
      categories=[
        _Category(
          index=0,
          score=0.486573,
          display_name='',
          category_name='Negative'),
        _Category(
          index=0,
          score=0.513427,
          display_name='',
          category_name='Positive'
        )
      ],
      head_index=0,
      head_name=''
    )])


class ModelFileType(enum.Enum):
  FILE_CONTENT = 1
  FILE_NAME = 2


class NLClassifierTest(parameterized.TestCase, tf.test.TestCase):

  @parameterized.parameters(
      # Regex tokenizer model.
      (_REGEX_TOKENIZER_MODEL, ModelFileType.FILE_NAME, _POSITIVE_INPUT,
       _EXPECTED_RESULTS_OF_POSITIVE_INPUT),
      (_REGEX_TOKENIZER_MODEL, ModelFileType.FILE_CONTENT, _POSITIVE_INPUT,
       _EXPECTED_RESULTS_OF_POSITIVE_INPUT))
  def test_classify_model(self, model_name, model_file_type, text,
                          expected_classification_result):
    # Creates classifier.
    model_path = test_util.get_test_data_path(model_name)
    if model_file_type is ModelFileType.FILE_NAME:
      base_options = _BaseOptions(file_name=model_path)
    elif model_file_type is ModelFileType.FILE_CONTENT:
      with open(model_path, "rb") as f:
        model_content = f.read()
      base_options = _BaseOptions(file_content=model_content)
    else:
      # Should never happen
      raise ValueError('model_file_type is invalid.')

    options = _NLClassifierOptions(base_options=base_options)
    classifier = _NLClassifier.create_from_options(options)
    # Classifies text using the given model.
    text_classification_result = classifier.classify(text)
    self.assertProtoEquals(text_classification_result.to_pb2(),
                           expected_classification_result.to_pb2())


if __name__ == "__main__":
  tf.test.main()
