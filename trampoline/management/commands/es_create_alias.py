"""
Management command for trampoline.
"""
from trampoline.management.base import ESBaseCommand


class Command(ESBaseCommand):
    help = (
        "Create an alias from {0}{1}INDEX_NAME{2} to {0}{1}TARGET_NAME{2}."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index_name'],
        ESBaseCommand.options['target_name'],
        ESBaseCommand.options['using']
    )
    required_options = ('index_name', 'target_name')

    def run(self, *args, **options):
        using = self.using

        if not self.dry_run:
            self.trampoline_config.get_connection(using).indices.put_alias(
                index=self.target_name,
                name=self.index_name
            )
        self.print_success(u"Created alias from '{0}' to '{1}'.".format(
            self.index_name, self.target_name))
