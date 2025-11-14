from django.core.management.base import BaseCommand
from teams.models import Team

class Command(BaseCommand):
    help = 'Recalcula los puntajes de todos los equipos'

    def handle(self, *args, **options):
        teams = Team.objects.all()
        
        self.stdout.write(self.style.WARNING(f'Recalculando puntajes de {teams.count()} equipos...'))
        
        for team in teams:
            old_score = team.total_score
            team.update_score()
            new_score = team.total_score
            
            if old_score != new_score:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {team.name}: {old_score} → {new_score} puntos')
                )
            else:
                self.stdout.write(f'  {team.name}: {new_score} puntos (sin cambios)')
        
        self.stdout.write(self.style.SUCCESS('\n¡Puntajes recalculados exitosamente!'))
