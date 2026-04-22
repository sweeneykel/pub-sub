import pytest
from project.message import Message

# If you want the core set only, write these first:
#
# subclass can initialize correctly
# type == "publish"
# topic comes from child
# event_id comes from child
# to_json() produces valid JSON with expected fields
# missing _get_topic() raises
# missing _generate_event_id() raises

class TestMessage(Message):
    def _get_topic(self):
        return "image_submitted"

    def _generate_event_id(self):
        return "IS_1"

def test_base_class_raises_if_topic_not_implemented():
    class BadMessage(Message):
        def _generate_event_id(self):
            return "IS_1"

    with pytest.raises(NotImplementedError, match="Child class must define topic"):
        BadMessage({"x": 1})

def test_base_class_raises_if_event_id_not_implemented():
    class BadMessage(Message):
        def _get_topic(self):
            return "image_submitted"

    with pytest.raises(NotImplementedError, match="Child class must define event_id logic"):
        BadMessage({"x": 1})
