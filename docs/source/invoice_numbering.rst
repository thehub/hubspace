Invoice Numbering SChemes
=========================

:Deprecated old scheme: H<Invoice number>. eg. H1956

:New scheme: XXXYYYYYYY 
        - XXX Location ID
        - YYYYYYY Invoice number in series for that location
    eg. 120000745

Why new scheme
--------------
Old scheme creates the invoice number which are not continuous series for a location, which was legal problem for some locations. New scheme gurantees uninterrupted series. For eg. after 120000745 next invoice number would be 120000746. If you delete 120000746 before sending, the number would be reused.

Usage
-----
Navigate to Hosting->Administration.
Checking "New Invoice numbering scheme" checkbox on will enable new invoice numbering.
