import tldextract
import argparse
import dns.resolver
import dns.zone
import dns.query
import logging
import json

from . import readin

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check if name servers allow DNS zone transfer"
    )

    parser.add_argument(
        "domain",
        nargs="*",
        help="domain to check"
    )

    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output in JSON"
    )

    parser.add_argument(
        "-p",
        "--parent",
        action="store_true",
        help="Check parent domains"
    )

    parser.add_argument(
        "--one",
        action="store_true",
        help="Stop checking when one name server returns zone info",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="Verbosity",
        default=0
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    init_log(args.verbose)

    checked_domains = set()

    if args.json:
        print_zone = print_zone_json
    else:
        print_zone = print_zone_plain

    for domain in readin.read_targets(args.domain):
        if args.parent:
            domains_to_check = get_parent_domains(domain)
        else:
            domains_to_check = [domain]

        for domain in domains_to_check:
            if domain in checked_domains:
                break

            checked_domains.add(domain)

            logger.info("Checking %s", domain)
            for zone in get_zone(domain):
                print_zone(zone)
                if args.one:
                    break


def get_zone(domain):
    nameservers = get_nameservers(domain)
    logger.info("%s nameservers: %s", domain, ",".join(nameservers))
    for ns in nameservers:
        try:
            zone = resolve_zone(domain, ns)
            yield zone
        except dns.exception.FormError:
            logger.info(
                "No zone transfer allowed in %s for %s",
                ns,
                domain,
            )


def get_nameservers(domain):
    try:
        nameservers = resolve_nameservers(domain)
        return nameservers
    except dns.resolver.NoAnswer:
        logger.error("No nameservers for %s", domain)
    except dns.resolver.NXDOMAIN as e:
        logger.error(
            "No able to retrieve name servers for %s: %s",
            domain,
            e
        )

    return []


def print_zone_json(zone):
    print(json.dumps(zone))


def print_zone_plain(zone):
    msg = [
        "###### Zone {} ######".format(zone["domain"]),
        "Domain: {}".format(zone["domain"]),
        "Nameserver: {}".format(zone["nameserver"]),
        "Records::",
    ]

    for record in zone["records"]:
        msg.append("{} {} {} {}".format(
            record["name"],
            record["class"],
            record["type"],
            record["data"]
        ))

    print("\n{}".format("\n".join(msg)))


def resolve_zone(domain, ns):
    ns_ip = resolve_ip(ns)
    records = resolve_zone_records(domain, ns_ip)
    return {
        "domain": domain,
        "nameserver": ns,
        "records": records
    }


def resolve_zone_records(domain, ns_ip):
    records = []
    z = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain))
    for node_name in sorted(z.nodes.keys()):
        name = node_name.concatenate(z.origin)
        node = z[node_name]
        for rdataset in node.rdatasets:
            for rr in rdataset.items.keys():
                records.append({
                    "name": str(name),
                    "class": rr.rdclass.name,
                    "type": rr.rdtype.name,
                    "data": str(rr)
                })

    return records


def resolve_ip(domain):
    ips = dns.resolver.resolve(domain, 'A')
    return str(ips[0])


def resolve_nameservers(domain):
    answer = dns.resolver.resolve(domain, 'NS')
    return [str(ns) for ns in answer]


def get_parent_domains(domain):
    domain_parts = tldextract.extract(domain)
    root_domain = "{}.{}".format(domain_parts.domain, domain_parts.suffix)
    parent_domains = [root_domain]

    parent_domain = root_domain

    sub_parts = domain_parts.subdomain.split(".")
    sub_parts.reverse()

    for sub_part in sub_parts:
        parent_domain = "{}.{}".format(sub_part, parent_domain)
        parent_domains.append(parent_domain)

    parent_domains.reverse()

    return parent_domains


def init_log(verbosity=0):

    if verbosity == 1:
        level = logging.INFO
    elif verbosity > 1:
        level = logging.DEBUG
    else:
        level = logging.WARN

    logging.basicConfig(
        level=logging.ERROR,
        format="%(levelname)s:%(message)s"
    )
    logger.level = level
