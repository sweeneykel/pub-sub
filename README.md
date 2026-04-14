# pub-sub

## Goal:
System that can upload a photo, generate and store annotations and vector embeddings. System that can search vector and document db for similar images or an image that matches a topic. Asynchronous with pub-sub architecture.

## Architecture for Image Search and Image Learning
[Link to Events and Messages outline](https://docs.google.com/spreadsheets/d/1IQb-8FlekCkqSglsvnialNid2d1lZciirRWZFQ1n6fs/edit?usp=sharing)

## Schematic (By Professor Alshaykh)
<img width="541" height="289" alt="ec530proj2schematic" src="https://github.com/user-attachments/assets/b504be03-e0fd-4629-a361-45adf53ddfdc" />

## Annotation and Embedding Connection Design Choice
Annotation and Embedding output can be kept separate or can be used to inform one another.
Annotation can pass labels to Embedding to help shape the embedding space; to tell the embedding service what to 
organize based on (semantic meaning or pixel similarity). 

## Redis Pub-Sub: Design Choice
(-)At most once delivery system. Will not reattempt if failure.

(-)'Fire and Forget' If not subscribers, message disappears

(+)Allows simultaneous processing. (No blocks) Unlike queuing.

(+)Ideal for scaling systems. Unlike point-to-point.

## Tools Used:
pub-sub, document db, vector db, asynchronous workflow, event generator for unit testing

## Concepts:



