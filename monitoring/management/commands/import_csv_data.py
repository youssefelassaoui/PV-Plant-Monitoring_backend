# monitoring/management/commands/import_csv_data.py

import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from monitoring.models import MeteorologicalData, ElectricalData, PVSystem

class Command(BaseCommand):
    help = 'Import CSV data into the database'

    def handle(self, *args, **kwargs):
        # Ensure PVSystem objects exist
        self.create_pv_systems()

        # Import data
        self.import_meteorological_data('/Users/youssef.elassaoui/downloads/meteo_data_cdc_scada.csv')
        self.import_electrical_data('/Users/youssef.elassaoui/downloads/data_prod_system1.csv', 1)
        self.import_electrical_data('/Users/youssef.elassaoui/downloads/data_prod_system2.csv', 2)
        self.import_electrical_data('/Users/youssef.elassaoui/downloads/data_prod_system3.csv', 3)
        
        self.stdout.write(self.style.SUCCESS('Successfully imported data'))

    def create_pv_systems(self):
        PVSystem.objects.get_or_create(
            id=1,
            defaults={
                'name': 'System 1',
                'capacity': 16.56,
                'inverter_type': 'Inverter Type 1',
                'number_of_panels': 69,
                'technology': 'Mono-Si',
                'year_of_installation': 2015
            }
        )
        PVSystem.objects.get_or_create(
            id=2,
            defaults={
                'name': 'System 2',
                'capacity': 5.25,
                'inverter_type': 'Inverter Type 2',
                'number_of_panels': 10,
                'technology': 'Half-cut Mono-Si',
                'year_of_installation': 2021
            }
        )
        PVSystem.objects.get_or_create(
            id=3,
            defaults={
                'name': 'System 3',
                'capacity': 2.34,
                'inverter_type': 'Inverter Type 3',
                'number_of_panels': 7,
                'technology': 'Half-cut Mono-Si',
                'year_of_installation': 2021
            }
        )

    def import_meteorological_data(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                timestamp = timezone.make_aware(datetime.strptime(row['Time'], '%m/%d/%Y %H:%M'))
                MeteorologicalData.objects.create(
                    time=timestamp,
                    gti=float(row['GTI']) if row['GTI'] else 0.0,
                    ghi=float(row['GHI']) if row['GHI'] else 0.0,
                    dni=float(row['DNI']) if row['DNI'] else 0.0,
                    dhi=float(row['DHI']) if row['DHI'] else 0.0,
                    air_temp=float(row['Air_Temp']) if row['Air_Temp'] else 0.0,
                    rh=float(row['RH']) if row['RH'] else 0.0,
                    pressure=float(row['Pressure']) if row['Pressure'] else 0.0,
                    wind_speed=float(row['Wind_speed']) if row['Wind_speed'] else 0.0,
                    wind_dir=float(row['wind_dir']) if row['wind_dir'] else 0.0,
                    wind_gust=float(row['wind_gust']) if row['wind_gust'] else 0.0,
                    rain=float(row['Rain']) if row['Rain'] else 0.0
                )

    def import_electrical_data(self, file_path, system_id):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            system = PVSystem.objects.get(id=system_id)
            for row in reader:
                timestamp = timezone.make_aware(datetime.strptime(row['Time'], '%Y-%m-%d %H:%M:%S'))
                ElectricalData.objects.create(
                    system=system,
                    time=timestamp,
                    adresse=int(float(row['Adresse'])) if row['Adresse'] else 0,
                    i1=float(row['I1']) if row['I1'] else 0.0,
                    u_dc=float(row['U_DC']) if row['U_DC'] else 0.0,
                    p_dc=float(row['P_DC']) if row['P_DC'] else 0.0,
                    t1=float(row['T1']) if row['T1'] else 0.0,
                    t2=float(row['T2']) if row['T2'] else 0.0,
                    i_sum=float(row['I_SUM']) if row['I_SUM'] else 0.0
                )
