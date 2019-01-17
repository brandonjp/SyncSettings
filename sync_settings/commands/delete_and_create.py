# -*- coding: utf-8 -*-

import sublime
import sublime_plugin

from .decorators import check_settings

from ..libs import settings
from ..libs.gist import Gist, NotFoundError
from ..libs.logger import logger
from ..thread_progress import ThreadProgress
from .. import sync_version as version


class SyncSettingsDeleteAndCreateCommand(sublime_plugin.WindowCommand):
    def delete_and_create(self, should_create=False):
        gid = settings.get('gist_id')
        try:
            Gist(settings.get('access_token')).delete(gid)
            settings.update('gist_id', '')
            # delete information related to the deleted gist
            version.update_config_file({})
            if should_create:
                self.window.run_command('sync_settings_create_and_upload')
                pass
        except NotFoundError:
            settings.update('gist_id', '')
        except Exception as e:
            logger.exception(e)
            sublime.message_dialog('Sync Settings:\n\n{}'.format(str(e)))

    @check_settings('gist_id', 'access_token')
    def run(self, create=True):
        dialog_message = (
            'Sync Settings:\n\n'
            'This action will delete your remote backup, do you want to proceed with this action?\n\n'
            'Note: this action is irreversible'
        )
        if sublime.yes_no_cancel_dialog(dialog_message) == sublime.DIALOG_YES:
            gid = settings.get('gist_id')
            ThreadProgress(
                target=lambda: self.delete_and_create(should_create=create),
                message='deleting gist `{}`'.format(gid),
                success_message='gist deleted'
            )
