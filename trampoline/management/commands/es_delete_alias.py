"""
Management command for trampoline.
"""
from trampoline.management.base import ESBaseCommand


class Command(ESBaseCommand):
    help = (
        "Delete the alias from {0}{1}INDEX_NAME{2} to {0}{1}TARGET_NAME{2}."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index_name'],
        ESBaseCommand.options['target_name'],
        ESBaseCommand.options['using']
    )
    required_options = ('index_name', 'target_name')

    def run(self, *args, **options):
        self.confirm(
            u"Are you really sure you want to delete the alias '{0}' ?"
            .format(self.index_name)
        )
        using = self.using

        if not self.dry_run:
            self.trampoline_config.get_connection(using).indices.delete_alias(
                index=self.target_name,
                name=self.index_name
            )
        self.print_success(u"Deleted alias '{0}' from '{1}'.".format(
            self.target_name, self.index_name))
