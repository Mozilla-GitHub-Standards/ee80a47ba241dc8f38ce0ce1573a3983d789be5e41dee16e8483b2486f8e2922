import logging
import subprocess

from django.core.management.base import BaseCommand, CommandError

from relops_hardware_controller.api.validators import validate_host


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '''Reboots a server with ssh. The account it uses should use
    ForceCommand to only run the reboot command. Raises an exception on
    timeout.'''
    doc_url = 'https://wiki.mozilla.org/Security/Guidelines/OpenSSH'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'hostname',
            type=str,
            help='Remote hostname to connect to.',
        )

        # Named (required) arguments
        parser.add_argument(
            '-l',
            dest='login_name',
            type=str,
            required=True,
            help='Specifies the user to log in as on the remote machine.',
        )
        parser.add_argument(
            '-i',
            dest='identity_file',
            type=str,
            required=True,
            help='Selects a file from which the identity (private key) for public key authentication is read.',
        )

        # Named (optional) arguments
        parser.add_argument(
            '-p',
            dest='port',
            type=int,
            default=22,
            help='Port to connect to on the remote host.',
        )

        # Not an ssh option
        parser.add_argument(
            '--timeout',
            dest='timeout',
            default=5,
            type=int,
            help='stop after N seconds',
        )

    def handle(self, hostname, *args, **options):
        validate_host(hostname)

        call_args = [
            'ssh',

            '-o', 'PasswordAuthentication=no',
            '-o', 'ServerAliveInterval=2',
            '-o', 'LogLevel=ERROR',

            # disable host key checks
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',

            '-i', options['identity_file'],
            '-l', options['login_name'],
            '-p', str(options['port']),
            hostname,
        ]
        logger.debug('ssh reboot with base args: {}'.format(' '.join(call_args)))

        # By trying a few different reboot commands we don't need to special case
        # different types of hosts. The "shutdown" command is for Windows, but uses
        # hyphens because it gets run through a bash shell. We also delay the
        # shutdown for a few seconds so that we have time to read the exit status
        # of the shutdown command.
        for reboot_cmd in ['reboot', 'shutdown -f -t 3 -r']:
            try:
                return subprocess.check_output(call_args + [reboot_cmd],
                                               stderr=subprocess.STDOUT,
                                               encoding='utf-8',
                                               timeout=options['timeout'])
            except subprocess.CalledProcessError as error:
                logger.info('{} ssh reboot with command {} failed: {}'.format(hostname, reboot_cmd, error))

        raise CommandError('{} All ssh reboot commands failed.'.format(hostname))
