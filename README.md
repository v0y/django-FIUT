Fine, Incredibly Useful Tools
=============================

helpers
-------

* `simple_send_email()` - send email in one (very long) line
* `get_page_and_paginator()` - get page with first and last few pages and paginator objects
* `slugify()` - better slugify - handle *ł* and *Ł*!
* `unix_time` - get unix time


forms
-----

* `SelectDateWithNoneWidget()` - select date with None form widget

  Example:
  ![select date widget](selectdate.png)


context processors
------------------
* `settings_values` - settings values in templates!

  Example usage:

  ```django
  {{ settings.DATABASES.default.PASSWORD }}
  ```
