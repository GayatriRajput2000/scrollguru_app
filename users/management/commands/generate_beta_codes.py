from django.core.management.base import BaseCommand
from users.models import BetaCode
import random
import string

class Command(BaseCommand):
    help = 'Generate 10 unique Beta Access Codes for ScrollGuru'

    def handle(self, *args, **options):
        codes_generated = 0
        existing_codes = set(BetaCode.objects.values_list('code', flat=True))

        self.stdout.write(self.style.WARNING('Generating 10 Beta Codes...'))

        while codes_generated < 10:
            # Generate random code like SG-BETA-XXXXXX
            code = 'SG-BETA-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            if code not in existing_codes:
                BetaCode.objects.create(code=code)
                existing_codes.add(code)
                codes_generated += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {code}'))

        self.stdout.write(self.style.SUCCESS('\n✅ 10 Beta Codes successfully generated!'))