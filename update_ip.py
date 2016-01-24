#! /usr/bin/env python

from __future__ import print_function

import click
import csv
import dreampylib
import getip
import logging


LOGGER = logging.getLogger('update_ip')


def _connect_api(server, key):
    connection = dreampylib.DreampyLib(user=server, key=key)

    if connection.is_connected():
        LOGGER.debug("Connected to DreamHost API. Server: {}".format(server))
        return connection
    else:
        LOGGER.error("Unable to connect to DreamHost API. Check server name and API key values.")
        exit()


def update_ip(server, key, ipaddr, fuzzy=None, connection=None):
    if fuzzy is None:
        fuzzy = False

    if connection is None:
        connection = _connect_api(server, key)
    else:
        server = connection._user
        key = connection._key

    LOGGER.info("Server: {}, Key: {}, IP: {}".format(server, key, ipaddr))
    
    result = connection.dns.list_records()

    if not result[0] == True:
        LOGGER.error('Problem retrieving DNS records')
        return 1

    retcodes = list()
    for record in result[2]:
        server_found = record['record']
        if fuzzy:
            was_server_found = (server in server_found)
        else:
            was_server_found = (server == server_found)
        if was_server_found and record['type'] == 'A':
            value = record['value']
            LOGGER.info('\'A\' record for {} found. Current IP: {}'.format(server_found, value))

            if value == str(ipaddr):
                LOGGER.info('Record is up to date with correct IP address.')
                retcodes.append(0)
                continue

            if record['editable'] != '1':
                LOGGER.debug('Record is not editable.')
                retcodes.append(1)
                continue

            LOGGER.debug('Removing record.')
            kwargs = dict(record=server_found, value=value, type='A')
            retcode = connection.dns.remove_record(**kwargs)[0]
            if not retcode:
                LOGGER.error('Problem removing record.')
                retcodes.append(1)
                continue

            LOGGER.debug('Adding updated record.')
            kwargs = dict(record=server_found, value=str(ipaddr), type="A")
            retcode = connection.dns.add_record(**kwargs)[0]
            if not retcode:
                LOGGER.error('Problem adding updated record.')
                retcodes.append(1)
                continue

            LOGGER.info('Successfully updated {} to {}'.format(server_found, ipaddr))
            retcodes.append(0)

    return any(retcodes)


@click.command()
@click.option('-f', '--filename', type=click.Path(exists=True), help='Comma-separated server,key file. If provided, overrides other options.')
@click.option('-s', '--server', type=str, help='Server\'s domain name. Multiple allowed.', multiple=True)
@click.option('-k', '--key', type=str, help='DreamHost API Key.')
@click.option('-i', '--ip', default=None, type=str, help='Desired A record value')
@click.option('--fuzzy', is_flag=True, help='Match all subdomains (e.g., www, ftp, ssh)')
def main(filename, server, key, ip, fuzzy):
    if not ip:
        ip = getip.get_external_ip()
    LOGGER.info('Using IP: {}'.format(ip))

    retcodes = list()
    if filename:
        LOGGER.info('File {} found'.format(filename))
        with open(filename, 'r') as domain_csv:
            reader = csv.reader(domain_csv, delimiter=',')
            for row in reader:
                retcode = update_ip(server=row[0], key=row[1], ipaddr=ip, fuzzy=fuzzy)
                retcodes.append(retcode)
    else:
        for server_id in server:
            retcode = update_ip(server=server_id, key=key, ipaddr=ip, fuzzy=fuzzy)
            retcodes.append(retcode)

    if any(retcodes):
        # There was an error
        return 1
    else:
        # Everything's a-ok
        return 0

if __name__ == '__main__':
    LOGGER = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    main()
