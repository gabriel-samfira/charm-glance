Overview
--------

This charm provides the Glance image service for OpenStack.  It is intended to
be used alongside the other OpenStack components.

Usage
-----

Glance may be deployed in a number of ways.  This charm focuses on 3 main
configurations.  All require the existence of the other core OpenStack
services deployed via Juju charms, specifically: mysql, keystone and
nova-cloud-controller.  The following assumes these services have already
been deployed.

Local Storage
=============

In this configuration, Glance uses the local storage available on the server
to store image data:

    juju deploy glance
    juju add-relation glance keystone
    juju add-relation glance mysql
    juju add-relation glance nova-cloud-controller

Swift backed storage
====================

Glance can also use Swift Object storage for image storage.  Swift is often
deployed as part of an OpenStack cloud and provides increased resilience and
scale when compared to using local disk storage.  This configuration assumes
that you have already deployed Swift using the swift-proxy and swift-storage
charms:

    juju deploy glance
    juju add-relation glance keystone
    juju add-relation glance mysql
    juju add-relation glance nova-cloud-controller
    juju add-relation glance swift-proxy

This configuration can be used to support Glance in HA/Scale-out deployments.

Ceph backed storage
===================

In this configuration, Glance uses Ceph based object storage to provide
scalable, resilient storage of images.  This configuration assumes that you
have already deployed Ceph using the ceph charm:

    juju deploy glance
    juju add-relation glance keystone
    juju add-relation glance mysql
    juju add-relation glance nova-cloud-controller
    juju add-relation glance ceph

This configuration can also be used to support Glance in HA/Scale-out
deployments.

NOTE: Glance acts as a Ceph client in this case which requires IP (L3)
connectivity to ceph monitors and OSDs. For MAAS-based deployments this
can be addressed with network spaces (see the relevant section below).

HA/Clustering
===================

There are two mutually exclusive high availability options: using virtual
IP(s) or DNS. In both cases, a relationship to hacluster is required which
provides the corosync back end HA functionality.

To use virtual IP(s) the clustered nodes must be on the same subnet such that
the VIP is a valid IP on the subnet for one of the node's interfaces and each
node has an interface in said subnet. The VIP becomes a highly-available API
endpoint.

At a minimum, the config option 'vip' must be set in order to use virtual IP
HA. If multiple networks are being used, a VIP should be provided for each
network, separated by spaces. Optionally, vip_iface or vip_cidr may be
specified.

To use DNS high availability there are several prerequisites. However, DNS HA
does not require the clustered nodes to be on the same subnet.
Currently the DNS HA feature is only available for MAAS 2.0 or greater
environments. MAAS 2.0 requires Juju 2.0 or greater. The clustered nodes must
have static or "reserved" IP addresses registered in MAAS. The DNS hostname(s)
must be pre-registered in MAAS before use with DNS HA.

At a minimum, the config option 'dns-ha' must be set to true and at least one
of 'os-public-hostname', 'os-internal-hostname' or 'os-internal-hostname' must
be set in order to use DNS HA. One or more of the above hostnames may be set.

The charm will throw an exception in the following circumstances:
If neither 'vip' nor 'dns-ha' is set and the charm is related to hacluster
If both 'vip' and 'dns-ha' are set as they are mutually exclusive
If 'dns-ha' is set and none of the os-{admin,internal,public}-hostname(s) are
set

Note that Glance in HA configuration must be used with either Ceph or
Swift providing backing image storage.

Glance metering
===============

In order to do Glance metering with Ceilometer, an AMQP relation is required
e.g.

    juju deploy glance
    juju deploy rabbitmq-server
    juju deploy ceilometer-agent
    ...
    juju add-relation glance rabbitmq-server
    juju add-relation glance ceilometer-agent
    ...

Network Space support
---------------------

This charm supports the use of Juju Network Spaces, allowing the charm to be bound to network space configurations managed directly by Juju.  This is only supported with Juju 2.0 and above.

API endpoints can be bound to distinct network spaces supporting the network separation of public, internal and admin endpoints.

Glance acts as a Ceph client and needs IP connectivity to Ceph monitors and OSDs. Binding the ceph endpoint to a space can solve this problem in case monitors and OSDs are located on a single L2 broadcast domain (if they are not, static or dynamic routes need to be used in addition to spaces).

Access to the underlying MySQL instance can also be bound to a specific space using the shared-db relation.

To use this feature, use the --bind option when deploying the charm:

    juju deploy glance --bind "public=public-space internal=internal-space admin=admin-space shared-db=internal-spacec ceph=ceph-access-space"

Alternatively, these can also be provided as part of a juju native bundle configuration:

    glance:
      charm: cs:xenial/glance
      num_units: 1
      bindings:
        public: public-space
        admin: admin-space
        internal: internal-space
        shared-db: internal-space
        ceph: ceph-access-space

NOTE: Spaces must be configured in the underlying provider prior to attempting to use them.

NOTE: Existing deployments using os-*-network configuration options will continue to function; these options are preferred over any network space binding provided if set.

Policy Overrides
================

This feature allows for policy overrides using the `policy.d` directory.  This
is an **advanced** feature and the policies that the OpenStack service supports
should be clearly and unambiguously understood before trying to override, or
add to, the default policies that the service uses.  The charm also has some
policy defaults.  They should also be understood before being overridden.

> **Caution**: It is possible to break the system (for tenants and other
  services) if policies are incorrectly applied to the service.

Policy overrides are YAML files that contain rules that will add to, or
override, existing policy rules in the service.  The `policy.d` directory is
a place to put the YAML override files.  This charm owns the
`/etc/keystone/policy.d` directory, and as such, any manual changes to it will
be overwritten on charm upgrades.

Overrides are provided to the charm using a Juju resource called
`policyd-override`.  The resource is a ZIP file.  This file, say
`overrides.zip`, is attached to the charm by:


    juju attach-resource glance policyd-override=overrides.zip

The policy override is enabled in the charm using:

    juju config glance use-policyd-override=true

When `use-policyd-override` is `True` the status line of the charm will be
prefixed with `PO:` indicating that policies have been overridden.  If the
installation of the policy override YAML files failed for any reason then the
status line will be prefixed with `PO (broken):`.  The log file for the charm
will indicate the reason.  No policy override files are installed if the `PO
(broken):` is shown.  The status line indicates that the overrides are broken,
not that the policy for the service has failed. The policy will be the defaults
for the charm and service.

Policy overrides on one service may affect the functionality of another
service. Therefore, it may be necessary to provide policy overrides for
multiple service charms to achieve a consistent set of policies across the
OpenStack system.  The charms for the other services that may need overrides
should be checked to ensure that they support overrides before proceeding.
