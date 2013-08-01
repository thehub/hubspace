===============
Migration Notes
===============

Third party systems that imports/exports hubspace data and are used by hubs
===========================================================================

SAGE
----
SAGE for accounting.

Hubs: Some of europian Hubs

Hubspace support: Export invoice data to SAGE format

Data format: `hubspace.controllers:invoice_list <https://github.com/thehub/hubspace/blob/master/hubspace/controllers.py>`_

The Piggybank
-------------
Online private NFC payment system that registers each consumption on the bar.

Hubs: Prague

Hubspace support: Usage import APIs. Integration work in progress.

Data format: `<http://members.the-hub.net/help/import_usages.html>`_

Google Calendar
---------------
To publish events calendar

Hubs: A few

Hubspace support: Export bookings in iCal format

Data format: iCal

Printer log parsing
-------------------
Hubs: Islington

Hubspace support: Create usages by importing printer logs

Core Data
=========
Below is list of important hubspace data structures. These structures are defined at hubspace/model.py. One can find all fields and properties of these data structures in this module. URL for the same is https://github.com/thehub/hubspace/blob/master/hubspace/model.py
Still here we have tried to list a few key attributes.

Each structure is available as persistent class in above mentioned module. In turn it abstracts a database table structure, and instances being rows as the case with most ORMs.

Location
--------
tablename: location

Coworking place also referred as hub and place.

    - vat: Default tax level
    - vat_included: Specifies if taxes are included are excluded

Resource
---------
tablename: resource

Resources which Hubs provide to it's members. Usage of these resources are recorded and billed. eg. Meeting room, printer, projector
    - vat_default: If tax level defined here it overrides location.vat_default
    - time_based: Based on usage calculation methods, resources are of two types time based and quantity based. For eg. Meeting Room is time based and Tea is quantity based

Tariff
------
Tariff is a special resource of type `tariff`. Tariff is a collection of pricings defined for resources available with the Hubs. Member's resource usages are charged as per the tariff at the time of usage. Guest tariff is the default tariff, also used for determining charges of resource for usages by members with no monthly tariff.

Pricing
-------
tablename: pricing

Price of a resource effective for specified start and end date. A pricing is always associated with a tariff.

User
----
tablename: tg_user

Member of one or more Hubs. User structure primarily contain below data
    - member profile
    - preferences
    - billing profile
        Billing mode has three options

        - Bill to profile i.e. use profile details such as address name etc. for billing
        - Custom billing details
        - Bill to some other member

        Mode is decided by looking at attributes billto and bill_to_profile

Group
-----
tablename: tg_group

Group and UserGroup holds member data of roles of a member at Hubs. Member has different roles at different Hubs. eg. Member, Host, Director. When a location (hub) is created these groups are created for that location.

Usage
-----
tablename: rusage

Billable usage of resource by member. If usage is a room booking done for a meeting, usage structure may further contains other information related to that meeting. This information is used in publishing the event. Also referred as booking.
    - invoice_id: invoice id if usage is invoiced else null
    - repetition_id: Id of recursive bookings series. It points to one of the existing booking from which other bookings are created.
    - confirmed: Indicates if a booking is confirmed. If set to 0 booking is considerred tentative.
    - resource_name: Booking/Event name
    - resource_description: Booking/Event description
    - user: Member
    - booked_date: Booking datetime
    - start: Start datetime
    - end_time: End datetime
    - public_field: Indicates whether to publish event on microsite
    - cancelled: Boolean set to 1 in case of booking cancellation

Message Customization
---------------------
tablename: message_customization

Hubs may customize outgoing email messages. This structure holds the information of such customization.

Invoice
-------
tablename: invoice

Invoice is collection of usages. This is generated against a period and sent to member. Payments made against invoices are not recorded in Hubspace.
    - sent: Invoice has two states unsent and sent. Only if sent holds a datetime value invoice is considered sent.
    - number: Invoices follows numbering scheme as described at http://members.the-hub.net/help/invoice_numbering.html


- active attribute is common to many objects. It indicates if the object is enabled or not.
