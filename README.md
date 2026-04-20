# pub-sub

## Goal:
System that can upload a photo, generate and store annotations and vector embeddings. System that can search vector and document db for similar images or an image that matches a topic. Asynchronous with pub-sub architecture.

## Architecture for Image Search and Image Learning
[Link to Events and Messages Schemas in Google Sheets](https://docs.google.com/spreadsheets/d/1IQb-8FlekCkqSglsvnialNid2d1lZciirRWZFQ1n6fs/edit?usp=sharing)

## Schematic (By Professor Alshaykh)
<img width="541" height="289" alt="ec530proj2schematic" src="https://github.com/user-attachments/assets/b504be03-e0fd-4629-a361-45adf53ddfdc" />

## Design Choices

### Coordination
* Reference: The Many Faces of Publish/Subscribe by P. Eugster et al.

Spatial Coupling: Do interacting parties know each other? Are all parties aware of other parties?

Scaling: What happens as the node number grows?


Temporal Coupling: Do nodes need to act at the same time?

Failure: What happens if a node crashes?


Synchronization Coupling: Are you blocking anyone?

#### Redis Pub-Sub: "Ephemeral Broadcast"
Best for: broadcasting updates in real-time, chat systems, IoT, notification event driven systems like ("do work", "update status" )
(+)Ideal for scaling systems. Streamlined set-up. Subscribe to topics not nodes.

(+)Allows simultaneous processing by all subscriber that receive message. 

(-)At most once delivery system. Will not reattempt if failure. 'Fire and Forget' If no subscribers, message disappears

(-)No built-in support for message acknowledgement 

(-/+)All subscribers receive the same message

#### Redis Streams: "Durable System Messaging"
Best for: systems requiring certainty of delivery or more complex message processing routines
(+) Built in persistence of messages through message streams (append-only logs of messages). A subscriber can access
message history if they connect late.

(+) Coordinated processing through Consumer Groups = idempotency.

(+) Build in queues hold messages until module is able to process. Accounts for different processing rates of separate modules

(-) More complex setup

### Separation of Concerns.
#### Module Class
Previously I have used procedural programming but for this project decided to implement OOP given that all of the modules
would need capability to form channels, subscribe, publish...etc  This introduced some new things around defining what a
class is responsible for (and what it is not responsible for) and how to communicate this to a user. Also, separating 
concerns so that a component was only responsible for a small subset of behavior - hopefully making debugging and 
testing easier. 

This was suggested by ChatGPT when I asked it to code review what I had so far. The feedback was that presently I had a
single class which handled multiple concerns and therefore a dependency was spread throughout a system instead of being
isolated at one point.

[Infrastructure]
    Redis
[Integration Layer]
    RedisListener (class): handles I/O (subscribe, receive messages)
[Transport Layer]
    Queue: buffer + boundary
[Application Layer]
    Module (class): processes messages. This class doesn’t know about Redis. Doesn’t know about networking. Doesn’t know about
other modules. It just consumes messages from a queue.

The advantages it gave that seemed most compelling were the below;
* swap Redis → Kafka later (modules unchanged). Redis becomes replaceable infrastructure.
* test modules without Redis
* queues give backpressure control. If processing is slow: you can detect it and you can scale workers

The disadvantages were;
* might be overly complex for a small system

### Threading vs Asyncio vs Processes
#### Threading
Threads are lightweight execution units within a process. Due to the GIL, Python threads do not execute CPU-bound Python 
code in parallel. However, for I/O-bound tasks (like waiting for messages), threads release the GIL while waiting, 
allowing other threads to run. This is why threading is effective for I/O concurrency despite the GIL.
(+) OS handles switching between tasks when CPU bound. Less complexity.
(-) Race conditions
Kept threading out of APIs so that this "service" was provided as a part of joining the system.

#### Asyncio
(+) Programmer explicitly describes how task switching occurs which can lead to...
(+) ...more intentional control...
(-) ...but also complexity

## Tools Used
pub-sub, document db, vector db, asynchronous workflow, event generator for unit testing

## Concepts

## References
The Many Faces of Publish/Subscribe by P. Eugster et al.
https://systems.cs.columbia.edu/ds2-class/papers/eugster-pubsub.pdf

Professor Alshaykh's Lecture Notes


