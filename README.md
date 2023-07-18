# UK NOTAM Archive
An hourly updated archive of all UK Notices To Airmen (NOTAM), along with all other pre-flight information bulletins (PIB) and briefing sheets.

The data is fetched from the [NATS AIS Contingency system](https://www.nats.aero/do-it-online/pre-flight-information-bulletins/) as it provides the feeds without authentication.

Machine Readable
---

* [Full UK PIB - XML format](data/PIB.xml)

NATS says: ``The above file contains all UK NOTAM valid at the time of generation and within the next 7 days, it is provided by the EAD system with no declared xml schema and therefore may be subject to change with minimal notification.``

Human Readable
---

* [London FIR IFR/VFR Bulletin](https://jonty.github.io/uk-notam-archive/html/pib3.shtml)
* [Scottish FIR IFR/VFR Bulletin](https://jonty.github.io/uk-notam-archive/html/pib4.shtml)
* [Notifiable Danger Areas and Restricted Areas (Temporary)](https://jonty.github.io/uk-notam-archive/html/pib5.shtml)
* [Navigation Warnings](https://jonty.github.io/uk-notam-archive/html/pib6.shtml)
* [Aerodromes from 54N &nbsp;to 55N &amp; Scottish FIR](https://jonty.github.io/uk-notam-archive/html/pib54n.shtml)
* [Aerodromes from 53N to 54N](https://jonty.github.io/uk-notam-archive/html/pib53n.shtml)
* [Aerodromes from 52N to 53N](https://jonty.github.io/uk-notam-archive/html/pib52n.shtml)
* [Aerodromes from 51N to 52N](https://jonty.github.io/uk-notam-archive/html/pib51n.shtml)
* [Aerodromes from 50N to 51N inc Channel Isles](https://jonty.github.io/uk-notam-archive/html/pib50n.shtml)

PDF Briefing Sheets for situations of operational significance can be found in the [briefing_sheets](briefing_sheets) directory.

Todo:
--
* Break out NOTAMs into individual files identified by their ID
* Parse NOTAMs into a sane format
