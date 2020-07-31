import configparser
import getpass
import logging
import os
from urllib.parse import urlparse, urlunparse

import pgpasslib
from click import UsageError

logger = logging.getLogger('ocdskingfisher.views.config')


def _add_pgpass_password(d):
    # Use the password from the PostgreSQL Password File, if not provided.
    if not d['password']:
        # https://pgpasslib.readthedocs.io/en/latest/
        try:
            password_pgpass = pgpasslib.getpass(d['host'], d['port'] or 5432, d['dbname'], d['user'])
            if password_pgpass is not None:
                d['password'] = password_pgpass
        except pgpasslib.FileNotFound:
            pass
        except pgpasslib.InvalidPermissions as e:
            logger.warning('Skipping PostgreSQL Password File: {}.\nTry: chmod 600 {}'.format(e, e.args[0]))
        except pgpasslib.InvalidEntry as e:
            logger.warning('Skipping PostgreSQL Password File: {}'.format(e))

    return d


def get_database_uri():
    """
    Returns the database connection URL.
    """
    params = get_connection_parameters()

    netloc = ''
    if params['user']:
        netloc += params['user']
    if params['password']:
        netloc += f":{params['password']}"
    if params['user'] or params['password']:
        netloc += '@'
    if params['host']:
        netloc += params['host']
    if params['port']:
        netloc += f":{params['port']}"

    return urlunparse(('postgresql', netloc, f"/{params['dbname']}", '', '', ''))


def get_connection_parameters():
    """
    Returns the database connection parameters as a dict.
    """
    database_url = os.getenv('KINGFISHER_VIEWS_DB_URI')
    if database_url:
        parts = urlparse(database_url)

        return _add_pgpass_password({
            'user': parts.username,
            'password': parts.password,
            'host': parts.hostname,
            'port': parts.port,
            'dbname': parts.path[1:],
        })

    userpath = '~/.config/ocdskingfisher-views/config.ini'
    fullpath = os.path.expanduser(userpath)
    if not os.path.isfile(fullpath):
        raise UsageError('You must either set the KINGFISHER_VIEWS_DB_URI environment variable or create the {} file.'
                         '\nSee https://kingfisher-views.readthedocs.io/en/latest/get-started.html'.format(userpath))

    # Same defaults as https://github.com/gmr/pgpasslib/blob/master/pgpasslib.py
    default_username = getpass.getuser()
    default_hostname = 'localhost'

    config = configparser.ConfigParser()
    config.read(fullpath)

    username = config.get('DBHOST', 'USERNAME', fallback=default_username)
    password = config.get('DBHOST', 'PASSWORD', fallback='')
    hostname = config.get('DBHOST', 'HOSTNAME', fallback=default_hostname)
    try:
        port = config.getint('DBHOST', 'PORT', fallback=5432)
    except ValueError as e:
        raise UsageError('PORT is invalid in {}. ({})'.format(userpath, e))
    # We don't use the default database name (that matches the user name) as this is rarely what the user intends.
    dbname = config.get('DBHOST', 'DBNAME')

    # Instead of setting the database URL to "postgresql://:@:5432/dbname" (which implicitly uses the default
    # username and default hostname), we set it to, for example, "postgresql://morgan@localhost:5432/dbname".
    if not username:
        username = default_username
    if not hostname:
        hostname = default_hostname
    if not dbname:
        raise UsageError('You must set DBNAME in {}.'.format(userpath))

    return _add_pgpass_password({
        'user': username,
        'password': password,
        'host': hostname,
        'port': port,
        'dbname': dbname,
    })
