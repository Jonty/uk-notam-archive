# UK NOTAM Archive
An hourly updated archive of all UK Notices To Airmen (NOTAM), along with all other pre-flight information bulletins (PIB).

The data is fetched from the [NATS AIS Contingency system](https://www.nats.aero/do-it-online/pre-flight-information-bulletins/) as it provides the feeds without authentication.

Machine Readable
---

* [Full UK PIB - XML format](data/PIB.xml)

NATS says: ``The above file contains all UK NOTAM valid at the time of generation and within the next 7 days, it is provided by the EAD system with no declared xml schema and therefore may be subject to change with minimal notification.``

Human Readable
---

* [London FIR IFR/VFR Bulletin](html/pib3.shtml)
* [Scottish FIR IFR/VFR Bulletin](html/pib4.shtml)
* [Notifiable Danger Areas and Restricted Areas (Temporary)](html/pib5.shtml)
* [Navigation Warnings](html/pib6.shtml)
* [Aerodromes from 54N &nbsp;to 55N &amp; Scottish FIR](html/pib54n.shtml)
* [Aerodromes from 53N to 54N](html/pib53n.shtml)
* [Aerodromes from 52N to 53N](html/pib52n.shtml)
* [Aerodromes from 51N to 52N](html/pib51n.shtml)
* [Aerodromes from 50N to 51N inc Channel Isles](html/pib50n.shtml)

Todo:
--
* Break out NOTAMs into individual files identified by their ID
* Parse NOTAMs into a sane format
