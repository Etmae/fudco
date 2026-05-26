from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'One-time data migration from datadump.json to PostgreSQL'

    def handle(self, *args, **options):
        self.stdout.write("Clearing auto-generated ContentTypes...")
        ContentType.objects.all().delete()
        
        self.stdout.write("Loading datadump.json...")
        try:
            call_command('loaddata', 'datadump.json')
            self.stdout.write(self.style.SUCCESS("Data successfully migrated!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))