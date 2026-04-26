# this test class tests:
# correct perfect case
# assigns sequential IDs in FAISS for retrieval later
# rejects incorrect dimension vector embeddings
# rejects incorrect messages
# rejects vector embeddings that are not numbers
# accepts the format that the embedding arrives in (json in MessageClass)
# given a vector, correctly provides the NN to that vector

import json
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("faiss")

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import faiss
import VectorDB
from message import EmbeddingCreatedMessage, EmbeddingStoredMessage


class FakePublisher:
    def __init__(self):
        self.published_messages = []

    def publish_message(self, channel, message):
        self.published_messages.append((channel, message))

# from embedding service, the message that arrives at the Vector db to be stored
def make_message(image_id="img-1", embedding_data=None):
    if embedding_data is None:
        embedding_data = [0.1, 0.2, 0.3, 0.4, 0.5]

    return {
        "payload": {
            "image_metadata": {
                "image_id": image_id,
                "path": f"{image_id}.jpg",
                "source": "test",
            },
            "embedding_data": embedding_data,
        }
    }

# set dimension of FAISS (set at 5 right now for ease of testing)
def make_index():
    return faiss.IndexFlatL2(VectorDB.embedding_dimension)

# correct case
def test_vector_db_process_stores_valid_embedding_metadata_and_publishes():
    publisher = FakePublisher()
    index = make_index()
    metadata_store = {}
    message = make_message()

    VectorDB.vector_db_process(message, publisher, index, metadata_store)

    assert index.ntotal == 1
    assert metadata_store == {0: message["payload"]["image_metadata"]}

    stored_vector = index.reconstruct(0)
    expected_vector = np.array(message["payload"]["embedding_data"], dtype="float32")
    np.testing.assert_allclose(stored_vector, expected_vector)

    assert len(publisher.published_messages) == 1
    channel, published_message = publisher.published_messages[0]
    assert channel == "embedding_stored"
    assert isinstance(published_message, EmbeddingStoredMessage)
    assert published_message.payload == message["payload"]


def test_vector_db_process_assigns_sequential_faiss_ids():
    publisher = FakePublisher()
    index = make_index()
    metadata_store = {}

    messages = [
        make_message("img-1", [0, 0, 0, 0, 0]),
        make_message("img-2", [1, 1, 1, 1, 1]),
        make_message("img-3", [2, 2, 2, 2, 2]),
    ]

    for message in messages:
        VectorDB.vector_db_process(message, publisher, index, metadata_store)

    assert index.ntotal == 3
    assert list(metadata_store.keys()) == [0, 1, 2]
    assert metadata_store[0]["image_id"] == "img-1"
    assert metadata_store[1]["image_id"] == "img-2"
    assert metadata_store[2]["image_id"] == "img-3"
    assert len(publisher.published_messages) == 3


def test_vector_db_process_does_not_store_or_publish_wrong_dimension_embedding():
    publisher = FakePublisher()
    index = make_index()
    metadata_store = {}
    # 4 dimension embedding when only accepts 5
    message = make_message(embedding_data=[0.1, 0.2, 0.3, 0.4])

    VectorDB.vector_db_process(message, publisher, index, metadata_store)

    assert index.ntotal == 0
    assert metadata_store == {}
    assert publisher.published_messages == []


@pytest.mark.parametrize(
    "message",
    [
        {},
        {"payload": {}},
        {"payload": {"image_metadata": {"image_id": "img-1"}}},
        {"payload": {"embedding_data": [0.1, 0.2, 0.3, 0.4, 0.5]}},
    ],
)
def test_vector_db_process_does_not_store_or_publish_malformed_messages(message):
    publisher = FakePublisher()
    index = make_index()
    metadata_store = {}

    VectorDB.vector_db_process(message, publisher, index, metadata_store)

    assert index.ntotal == 0
    assert metadata_store == {}
    assert publisher.published_messages == []


def test_vector_db_process_does_not_store_or_publish_non_numeric_embedding():
    publisher = FakePublisher()
    index = make_index()
    metadata_store = {}
    message = make_message(embedding_data=["a", "b", "c", "d", "e"])

    VectorDB.vector_db_process(message, publisher, index, metadata_store)

    assert index.ntotal == 0
    assert metadata_store == {}
    assert publisher.published_messages == []


def test_vector_db_process_accepts_embedding_created_message_json_shape():
    publisher = FakePublisher()
    index = make_index()
    metadata_store = {}
    image_metadata = {"image_id": "img-from-message", "path": "img-from-message.jpg"}
    embedding_data = [0.5, 0.4, 0.3, 0.2, 0.1]
    created_message = EmbeddingCreatedMessage(image_metadata, embedding_data)

    VectorDB.vector_db_process(
        json.loads(created_message.to_json()),
        publisher,
        index,
        metadata_store,
    )

    assert index.ntotal == 1
    assert metadata_store[0] == image_metadata
    assert len(publisher.published_messages) == 1
    channel, stored_message = publisher.published_messages[0]
    assert channel == "embedding_stored"
    assert stored_message.payload["image_metadata"] == image_metadata
    assert stored_message.payload["embedding_data"] == embedding_data


def test_stored_embeddings_support_expected_nearest_neighbor_search():
    publisher = FakePublisher()
    index = make_index()
    metadata_store = {}

    VectorDB.vector_db_process(
        make_message("near-zero", [0, 0, 0, 0, 0]),
        publisher,
        index,
        metadata_store,
    )
    VectorDB.vector_db_process(
        make_message("medium", [1, 1, 1, 1, 1]),
        publisher,
        index,
        metadata_store,
    )
    VectorDB.vector_db_process(
        make_message("far", [10, 10, 10, 10, 10]),
        publisher,
        index,
        metadata_store,
    )

    query = np.array([[0.1, 0, 0, 0, 0]], dtype="float32")
    distances, ids = index.search(query, k=1)

    assert ids[0][0] == 0
    assert distances[0][0] == pytest.approx(0.01)
    assert metadata_store[ids[0][0]]["image_id"] == "near-zero"
