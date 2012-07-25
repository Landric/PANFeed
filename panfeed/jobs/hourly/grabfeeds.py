from django_extensions.management.jobs import BaseJob
from panfeed.management.commands.grabfeeds import Command as GrabFeeds
from haystack.management.commands.update_index import Command as UpdateIndex
class Job(BaseJob):
    help = "Grab feeds and update"

    def execute(self):
        GrabFeeds().handle()
        UpdateIndex().handle()
        pass
