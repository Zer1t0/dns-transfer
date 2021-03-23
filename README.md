# dns-transfer

An utility to check zone transfer for domains.

## Usage

It only requires a domain to being given:

```shell
$ dns-transfer internal.zonetransfer.me

###### Zone internal.zonetransfer.me ######
Domain: internal.zonetransfer.me
Nameserver: intns1.zonetransfer.me.
Records::
internal.zonetransfer.me. IN SOA intns1.zonetransfer.me. robin.digi.ninja. 2014101601 172800 900 1209600 3600
internal.zonetransfer.me. IN NS intns1.zonetransfer.me.
cisco1.internal.zonetransfer.me. IN A 10.1.1.254
cisco2.internal.zonetransfer.me. IN A 10.1.1.253
dc.internal.zonetransfer.me. IN A 10.1.1.1
fileserv.internal.zonetransfer.me. IN A 10.1.1.4
mail.internal.zonetransfer.me. IN A 10.1.1.3
```

## Installation

```shell
pip3 install git+https://github.com/zer1t0/dns-transfer.git
```


## More cases

Getting a JSON output:
```shell
dns-transfer -j <domain>
```

Check parent domains:
```shell
dns-transfer -p dc.internal.zonetransfer.me
```

This will check:
- dc.internal.zonetransfer.me
- internal.zonetransfer.me
- zonetransfer.me

