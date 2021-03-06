- [Quality of Service Module](#quality-of-service-odule)
  - [QoS Profile](#qos-profile)
  - [Latency](#latency)
  - [Jitter](#jitter)
  - [Packet Loss](#packet-loss)
  - [Metrics](#metric-collection)

# Quality of Service Module

  ![alt text](../figures/HB_QoS_Module.png "Altering QoS")

The QOS module is situated inside the proxy processing pipline so as to :apply a given QoS profile to proxy traffic.
When the QoS module is started the given `session_id` is used to retrieve the QoS profile from `mongo`.
The QoS profile is retrieved from information contained within the session document, specifically the `serverOverload.id`

### Example session document
```json
{
  "name": "Session A",
  "description": "This is a description for a Session",
  "upstreamHost": "github.com",
  "upstreamPort": 80,
  "createdAt": "2014-02-12 03:34:51",
  "updatedAt": "2014-02-12 03:34:51",
  "testPlan":
  {
    "id": 12,
    "name": "ViPR Test plan"
  },
  "qos":
  {
    "id": 45
  },
  "serverOverload":
  {
    "id": 951
  },
  "user":
  {
    "id": 1,
    "username": "John Doe"
  },
  "executions": 42,
}
```

The `qos.id` is then used to make a secod query to retrieve the quality of service profile.
When the module receives a response or request, each QoS quality is applied to the traffic as defined by the retrieved QoS profile.

## QoS Profile

 The QoS profile can currently support three service quality types: latency, jitter and traffic loss.
Three qualities are implemented and applied to the http proxy traffic with the parameters given by the QoS_profile as follows:

| Feature     | Context | Description                                                                                                           |
|:------------|:--------|:----------------------------------------------------------------------------------------------------------------------|
| Latency     | request | Injectes a constant wait time into the the traffic stream so as to increase the round-trip time of each request       |
| Jitter      | request | Injects random wait time into the traffic stream so as to increase the round-trip time of each request inconsistently |
| Packet Loss | both    | Drops requests/responses randomly                                                                                     |
|             |         |                                                                                                                       |
### Example JSON representation:

```json
{
    "createdAt": "2014-02-12 03:34:51",
    "updatedAt": "2014-02-12 03:34:51",
    "latency": 100,
    "jitter": {
        "min": 30,
        "max": 50
    },
    "trafficLoss": 0.1
}
```
E.g. trafficLoss=0.1 means that the module will drop 10% of the traffic.

E.g. latency=100ms and jitter(min=30ms, max=50ms) means that latency will vary from 70ms to 150ms.

## Latency

The `latency` quality has the following parameters.

| Element | Context | Description                                        |
|:--------|:--------|:---------------------------------------------------|
| delay   | request | The delay, in miliseconds, the module will inject. |
|         |         |                                                    |

## Jitter

The `Jitter` quality has the following parameters.

| Element | Context | Description                                                          |
|:--------|:--------|:---------------------------------------------------------------------|
| maximum | request | The maximum amount of delay, in miliseconds, the module will inject. |
| minimum | request | The minimum amount of delay, in miliseconds, the module will inject. |

## Packet Loss

The `Packet Loss` quality has the following parameters.

| Element | Context | Description                                                         |
|:--------|:--------|:--------------------------------------------------------------------|
| chance  | both    | The percentage chance that any given request/response will be lost. |

#Metric Collection

The QOS module will continuously update a set of metrics that may be useful in future analysis of the injection session. Each metrics is available in real-time by making the module `status` API call. The following metrics are collected:

| metric      | Description                                             |
|:------------|:--------------------------------------------------------|
| lagtime     | The current amount of delay being injected              |
| packet-loss | The current total number of packets that have been lost |
