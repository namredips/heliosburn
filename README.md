# HeliosBurn

Helios Burn is a REST fault injection platform that captures HTTP and HTTPS traffic and logs it for users to review.
Helios Burn provides the capability to modify HTTP traffic, thus injecting faults, as it is being sent by the client
or received from the server. The purpose of Helios Burn is to provide developers with a tool that inject failures and
instabilities so that they can verify the stability and resilience of their applications and identify and prevent
failures before deploying them into a production environment.


Helios Burn can be deployed in a standalone server, in a Virtual Machine, or co-located with the Web server or Client
application.

It implements a man-in-the-middle interception using self-signed certificates to be able to intercept and interpret
HTTPS traffic.

![Helios-Burn-Overview](https://github.com/emccode/HeliosBurn/blob/master/docs/figures/Helios-Burn-Overview.png "Helios Burn Overview")


In general terms, the traffic flow is as follows:

1. The Helios Burn proxy gets requests from clients that are willing to access resources exposed by a REST application running on a web server (e.g. Amazon S3, OpenStack Swift, EMC Atmos, etc...).
2. The proxy processes the request performing modification depending on certain criteria.
3. The proxy forwards the processed request to the server on behalf of the client.
4. The proxy receives the response from the server.
5. The proxy processes the response performing modifications depending on certain criteria
6. The proxy returns the processed response to the client on behalf of the server.


## For Developers

The best way to get started with HeliosBurn development is taking a look at the [DEVELOPERS.md](DEVELOPERS.md) file. The document will walk you through setting up a development environment in a Vagrant box and configure PyCharm use it. This environment is ideal because it contains all needed packages and tools required by HeliosBurn.

If you would like to start contributing, check out these [notes](CONTRIBUTING.md) to help you get started.

### Code Organization

- docs/: Documentation
- heliosburn/: HeliosBurn core code
  - django/: Django project that encompasses the WebUI and the API
  - proxy/: Proxy engine
  - fault-injection/: Fault Injection engine and module
  - recorder/: Recorder engine and module
  - db_model: Database model
- puppet/: Puppet configuration and modules

### Data Flow

The core of HeliosBurn is a Twisted reactor that listens for TCP connections. The entry point of the proxy is a Twisted resource called `HeliosBurnResource` located in `heliosburn/proxy/proxy_core.py`. From there, the `HeliosBurnRequest` takes care of all incoming requests by passing them through all enabled modules and eventually establishing a connection with the upstream server and sending them through. Responses are handled by the `HeliosBurnClient` and, again, passed to the modules and back to clients.

## For Deployers

TODO
