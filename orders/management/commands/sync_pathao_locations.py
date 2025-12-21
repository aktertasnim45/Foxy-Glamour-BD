"""
Django management command to sync Pathao location data (cities and zones)
Usage: python manage.py sync_pathao_locations
"""

from django.core.management.base import BaseCommand
from orders.pathao import PathaoClient
from orders.models import PathaoCity, PathaoZone


class Command(BaseCommand):
    help = 'Sync Pathao cities and zones from API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cities-only',
            action='store_true',
            help='Only sync cities, not zones',
        )
        parser.add_argument(
            '--city-id',
            type=int,
            help='Sync zones for a specific city ID only',
        )

    def handle(self, *args, **options):
        client = PathaoClient()
        
        # Sync cities
        self.stdout.write('Fetching cities from Pathao API...')
        try:
            cities = client.get_cities()
            self.stdout.write(f'Found {len(cities)} cities')
            
            cities_created = 0
            cities_updated = 0
            
            for city_data in cities:
                city, created = PathaoCity.objects.update_or_create(
                    city_id=city_data.get('city_id'),
                    defaults={'city_name': city_data.get('city_name', '')}
                )
                if created:
                    cities_created += 1
                else:
                    cities_updated += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'Cities: {cities_created} created, {cities_updated} updated'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to sync cities: {e}'))
            return
        
        if options['cities_only']:
            return
        
        # Sync zones
        if options['city_id']:
            cities_to_sync = PathaoCity.objects.filter(city_id=options['city_id'])
        else:
            cities_to_sync = PathaoCity.objects.all()
        
        total_zones_created = 0
        total_zones_updated = 0
        
        for city in cities_to_sync:
            self.stdout.write(f'Fetching zones for {city.city_name}...')
            try:
                zones = client.get_zones(city.city_id)
                
                for zone_data in zones:
                    zone, created = PathaoZone.objects.update_or_create(
                        zone_id=zone_data.get('zone_id'),
                        defaults={
                            'zone_name': zone_data.get('zone_name', ''),
                            'city': city
                        }
                    )
                    if created:
                        total_zones_created += 1
                    else:
                        total_zones_updated += 1
                
                self.stdout.write(f'  - {len(zones)} zones')
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f'Failed to sync zones for {city.city_name}: {e}'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'Zones: {total_zones_created} created, {total_zones_updated} updated'
        ))
        
        self.stdout.write(self.style.SUCCESS('Pathao location sync complete!'))
