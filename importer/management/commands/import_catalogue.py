from django.core.management.base import BaseCommand, CommandError
import untangle


class Command(BaseCommand):
    help = 'Import data for catalogue'

    def add_arguments(self, parser):
         # Named (optional) arguments
        parser.add_argument('--file',
            action='store_true',
            dest='file',
            default='catalogue.xml',
            help='Name of the XML file to import')

    def handle(self, *args, **options):
            file = options.get('file')
            obj = untangle.parse(file)
            for p in obj.xml.produkty.produkt:
                pass
            self.stdout.write('Successfully imported data')