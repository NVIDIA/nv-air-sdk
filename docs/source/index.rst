NVIDIA Air SDK
==============

A Python SDK for creating, running, and managing network simulations on
`NVIDIA Air <https://air-ngc.nvidia.com>`_.

Installation
------------

The package is available on `PyPI <https://pypi.org/project/nv-air-sdk/>`_.

.. code-block:: bash

   pip install nv-air-sdk

Or with `uv <https://docs.astral.sh/uv/>`_:

.. code-block:: bash

   uv add nv-air-sdk

Requires Python 3.10+.

Authentication
--------------

The SDK supports three authentication methods. See the
`NVIDIA Air authentication guide <https://docs.nvidia.com/networking-ethernet-software/nvidia-air-v2/Authentication/>`_
for details on obtaining credentials.

**API Key** — pass an NGC Scoped API Key (SAK) directly:

.. code-block:: python

   from air_sdk import AirApi

   api = AirApi.with_api_key(api_key='nvapi-xxxx')

**NGC Config** — reads the key from ``~/.ngc/config``, created by
``ngc config set`` (requires the `NGC CLI <https://org.ngc.nvidia.com/setup/installers/cli>`_):

.. code-block:: python

   api = AirApi.with_ngc_config()
   # or equivalently:
   api = AirApi()

**Device Login** — opens a browser for interactive NGC authentication
(no pre-existing key required):

.. code-block:: python

   api = AirApi.with_device_login(
       email='user@nvidia.com',
       org_num='my-org',
   )

Non-Standard Hostnames
^^^^^^^^^^^^^^^^^^^^^^

All factory methods accept an ``api_url`` parameter that defaults to the
public NVIDIA Air instance. If you are connecting to a different Air
deployment, browse to ``/api`` on the host
(e.g. ``https://your-air-host.example.com/api``) and pass the API URL
from the servers dropdown to the SDK:

.. code-block:: python

   api = AirApi.with_api_key(
       api_key='nvapi-xxxx',
       api_url='https://your-air-host.example.com',
   )

Quick Start
-----------

.. code-block:: python

   from air_sdk import AirApi

   api = AirApi.with_api_key(api_key='nvapi-xxxx')

   # List simulations
   for sim in api.simulations.list():
       print(sim.name, sim.state)

   # Create a simulation
   sim = api.simulations.create(name='my-sim')

Examples
--------

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index

API Reference
-------------

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/air_sdk/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
