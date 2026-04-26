# pub-sub

## Video: Architecture walkthrough and Demo
[Video Here](https://drive.google.com/file/d/1bs3XysukzUeh8NRAmNYxszCUYcz9gQlb/view?usp=drive_link)

## Goal

This project is an asynchronous pub-sub prototype for image upload, image annotation, metadata storage, vector embedding storage, and image/topic search workflows.

The intended system can:

- Upload a photo.
- Generate or collect image annotations.
- Store annotation metadata in a document database.
- Store image embeddings in a vector database.
- Search for similar images by image or topic.
- Use event-driven pub-sub messages to decouple each module.

## Current Implementation Notes

- The services are designed to be run as separate Python processes.
- Redis is used for event transport.
- Each subscriber places received messages into an internal queue.
- Queue workers process messages asynchronously on background threads.
- Current service scripts run for about 60 seconds, then stop.
- The annotation workflow is manual and uses OpenCV windows plus terminal input.
- The MongoDB annotation service stores the full event payload.
- The Faiss vector database is currently in-memory only.
- Search result handling is not yet implemented.
- Embedding generation is not yet implemented.


## Architecture for Image Search and Image Learning

[Link to Events and Messages Schemas in Google Sheets](https://docs.google.com/spreadsheets/d/1IQb-8FlekCkqSglsvnialNid2d1lZciirRWZFQ1n6fs/edit?usp=sharing)

## Schematic

Schematic by Professor Osama Alshaykh:

<img width="541" height="289" alt="ec530proj2schematic" src="https://github.com/user-attachments/assets/b504be03-e0fd-4629-a361-45adf53ddfdc" />

## Tools Used

- Redis pub-sub
- Document database: MongoDB
- Vector database: Faiss
- Asynchronous workflow
- Event generator / message classes for unit testing
- OpenCV-based manual annotation GUI

## Project Structure

```text
project/
  main.py                  # CLI entry point for uploading/querying images
  PhotoUploadModule.py     # Photo upload and query publisher module
  message.py               # Pub-sub message classes and message schemas
  RedisPublisher.py        # Redis publisher wrapper
  RedisSubscriber.py       # Redis subscriber wrapper
  QueueWorker.py           # Threaded queue workers used by services
  AnnotModule.py           # Annotation service: consumes image submissions
  AnnotGUI.py              # OpenCV helper for manual bounding-box annotation
  AnnotDB.py               # MongoDB annotation storage service
  VectorDB.py              # Faiss vector storage service
  db.py                    # Utility script to print stored Mongo records
  logger.py                # Shared logging helper
  photos/                  # Sample images and uploaded images
  annotated_uploads/       # Annotated output images
  tests/                   # Pytest tests
```

## Requirements

Declared dependency:

```text
redis
```

Additional dependencies used by the code:

```text
pymongo
opencv-python
numpy
faiss-cpu
pytest
```

External services:

- Redis server running on `localhost:6379`
- MongoDB server running on `localhost:27017`

## Installation

From the repository root:

```bash
pip install redis pymongo opencv-python numpy faiss-cpu pytest
```

If using a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install redis pymongo opencv-python numpy faiss-cpu pytest
```

## How to Run

Start Redis before running the publisher/subscriber modules.

Start MongoDB before running the annotation database module.

### Run the CLI

From the repository root:

```bash
python project/main.py
```

The CLI supports:

```text
1) Upload file
2) Find k similar items by topic
3) Find k similar items by image
4) Exit
```

Uploading an image copies it into:

```text
project/photos/photo_uploads/
```

and publishes an `image_submitted` message.

### Run the Annotation Service

In a separate terminal:

```bash
python project/AnnotModule.py
```

This service subscribes to `image_submitted`, opens the uploaded image in an OpenCV annotation interface, asks the user for bounding-box coordinates and a label, saves the annotated image, then publishes `inference_completed`.

Annotated images are saved to:

```text
project/annotated_uploads/
```

### Run the Annotation Database Service

In a separate terminal, with MongoDB running:

```bash
python project/AnnotDB.py
```

This service subscribes to `inference_completed`, stores annotation metadata in MongoDB, then publishes `annotation_stored`.

MongoDB configuration:

```text
mongodb://localhost:27017/
database: annotation_db_01
collection: table_01
```

### Run the Vector Database Service

In a separate terminal:

```bash
python project/VectorDB.py
```

This service subscribes to `embedding_created`, stores embeddings in an in-memory Faiss index, stores metadata in an in-memory dictionary, then publishes `embedding_stored`.

The current Faiss index uses:

```text
IndexFlatL2
embedding_dimension = 5
```

### View MongoDB Records

```bash
python project/db.py
```

### Run Tests

From the repository root:

```bash
pytest
```

## Runtime Workflow

The current implemented event flow is:

```text
Photo CLI
  -> image_submitted
  -> Annotation Service
  -> inference_completed
  -> Annotation DB Service
  -> annotation_stored
```

The vector database flow is partially implemented:

```text
Embedding producer
  -> embedding_created
  -> Vector DB Service
  -> embedding_stored
```

The message classes for image and topic queries exist, and the CLI can publish query events, but query-result processing is not yet implemented.

## Modules

### `main.py`

Creates a Redis client and starts the photo CLI.

### `PhotoUploadModule.py`

Implements `PhotoCliModule`.

Responsibilities:

- Validate uploaded images by extension and MIME type.
- Copy uploaded images into `project/photos/photo_uploads/`.
- Publish image upload events.
- Publish image query events.
- Publish topic query events.

Supported image types:

```text
.jpg
.jpeg
.png
.gif
.webp
```

### `message.py`

Defines the base `Message` class and all current pub-sub message types.

Each message serializes to JSON with this structure:

```json
{
  "type": "publish",
  "topic": "topic_name",
  "event_id": "EVENT_ID",
  "payload": {}
}
```

### `RedisPublisher.py`

Wraps Redis publishing.

A publisher must register a channel before publishing to it. This helps catch accidental publishes to unsupported channels.

### `RedisSubscriber.py`

Wraps Redis subscription handling.

Each subscriber listens to one registered channel and pushes decoded JSON messages into a Python queue for worker processing.

### `QueueWorker.py`

Defines a base threaded queue worker and specialized workers:

- `AnnotationWorker`
- `AnnotationDBWorker`
- `VectorDBWorker`

Workers consume messages from queues and call service-specific processing functions.

### `AnnotModule.py`

Annotation service.

Subscribes to:

```text
image_submitted
```

Publishes to:

```text
inference_completed
```

It calls `user_annotates_image()` from `AnnotGUI.py` to gather bounding-box annotation metadata.

### `AnnotGUI.py`

OpenCV-based manual annotation helper.

It:

- Loads an image.
- Resizes it to width `600`.
- Displays a coordinate grid.
- Prompts the user for bounding-box coordinates and a label.
- Draws the annotation.
- Saves the annotated image.

Annotation metadata includes:

```text
name
upper_corner_x
upper_corner_y
lower_corner_x
lower_corner_y
annotation_label
```

### `AnnotDB.py`

MongoDB storage service.

Subscribes to:

```text
inference_completed
```

Publishes to:

```text
annotation_stored
```

Stores annotation payloads in MongoDB.

### `VectorDB.py`

Faiss vector database service.

Subscribes to:

```text
embedding_created
```

Publishes to:

```text
embedding_stored
```

Stores embeddings in a Faiss `IndexFlatL2` index and stores image metadata in an in-memory side table.

### `db.py`

Utility script that prints all records from the MongoDB annotation collection.

### `logger.py`

Shared logger configuration helper.

## Message Types

### `ImageSubmittedMessage`

Topic:

```text
image_submitted
```

Event ID prefix:

```text
IS_
```

Payload:

```json
{
  "image_id": "uuid",
  "path": "project/photos/photo_uploads/image.jpg",
  "source": "user_upload"
}
```

Published by:

```text
PhotoUploadModule.py
```

Consumed by:

```text
AnnotModule.py
```

### `AnnotationCompletedMessage`

Topic:

```text
inference_completed
```

Event ID prefix:

```text
IC_
```

Payload:

```json
{
  "image_metadata": {
    "image_id": "uuid",
    "path": "project/photos/photo_uploads/image.jpg",
    "source": "user_upload"
  },
  "annotation_metadata": {
    "name": "image",
    "upper_corner_x": 10,
    "upper_corner_y": 20,
    "lower_corner_x": 200,
    "lower_corner_y": 240,
    "annotation_label": "label"
  }
}
```

Published by:

```text
AnnotModule.py
```

Consumed by:

```text
AnnotDB.py
```

### `AnnotationStoredMessage`

Topic:

```text
annotation_stored
```

Event ID prefix:

```text
AS_
```

Payload:

```json
{
  "image_metadata": {}
}
```

Published by:

```text
AnnotDB.py
```

### `EmbeddingCreatedMessage`

Topic:

```text
embedding_created
```

Event ID prefix:

```text
EC_
```

Payload:

```json
{
  "image_metadata": {},
  "embedding_data": [0.1, 0.2, 0.3, 0.4, 0.5]
}
```

Expected consumer:

```text
VectorDB.py
```

Note: the message class exists, and the vector database service consumes this topic, but the embedding creation module is not currently implemented.

### `EmbeddingStoredMessage`

Topic:

```text
embedding_stored
```

Event ID prefix:

```text
ES_
```

Payload:

```json
{
  "image_metadata": {},
  "embedding_data": [0.1, 0.2, 0.3, 0.4, 0.5]
}
```

Published by:

```text
VectorDB.py
```

### `QueryImagesSubmitted`

Topic:

```text
query_images_submitted
```

Event ID prefix:

```text
QIS_
```

Payload:

```json
{
  "query_images_submitted": "path/to/query-image.jpg",
  "k": 5
}
```

Published by:

```text
PhotoUploadModule.py
```

Note: query processing is not currently implemented.

### `QueryTopicsSubmitted`

Topic:

```text
query_topics_submitted
```

Event ID prefix:

```text
QIS_
```

Payload:

```json
{
  "query_topics_submitted": "topic text",
  "k": 5
}
```

Published by:

```text
PhotoUploadModule.py
```

Note: query processing is not currently implemented.

