# pub-sub

## Goal:
System that can upload a photo, generate and store annotations and vector embeddings. System that can search vector and document db for similar images or an image that matches a topic. Asynchronous with pub-sub architecture.

## Events/Messages
[Link to Events and Messages outline](https://docs.google.com/spreadsheets/d/1IQb-8FlekCkqSglsvnialNid2d1lZciirRWZFQ1n6fs/edit?usp=sharing)

## Schematic (By Professor Alshaykh)


## Overall Architecture: Upload Image Task
**Upload Service/CLI**
Does: Uploads Image
Creates Event: image.submitted

**Image Processing/Image Service**
Listens to/Subscribes to: image.submitted
Does: Outline objects in a photo and tags identifier
Creates Event/Publishes: inference.completed

**Document db/Annotation Service**
Listens to/Subscribes to: inference.completed
Does: Stores locations of outline and tag in a json
Creates Event/Publishes: annotation.stored

**Embedding Service**
Listens to/Subscribes to: annotation.stored
Does: Makes an embedding (vector representation of an image)
Creates Event/Publishes: embedding.created

**Vector db/Index Service**
Listens to/Subscribes to: embedding.created
Does: stores embedding
Creates Event/Publishes: embedding.stored

**Upload Service/CLI**
Listens to/Subscribes to: embedding.stored
Does: Sends confirmation to user that task was successful

## Overall Architecture: Image Search Task

		TODO

## Redis Pub-Sub: Design Choice
(-)At most once delivery system. Will not reattempt if failure.
(-)'Fire and Forget' If not subscribers, message disappears
(+)Allows simultaneous processing. (No blocks) Unlike queuing.
(+)Ideal for scaling systems. Unlike point-to-point.

## Tools Used:
pub-sub, document db, vector db, asynchronous workflow, event generator for unit testing

## Concepts:



