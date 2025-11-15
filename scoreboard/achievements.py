# Sistema de Logros para CTF
from django.utils import timezone
from datetime import timedelta

class AchievementDefinition:
    """Definición de un logro"""
    def __init__(self, code, name, description, icon, category, check_func):
        self.code = code
        self.name = name
        self.description = description
        self.icon = icon
        self.category = category  # 'team' o 'individual'
        self.check_func = check_func

# Definiciones de logros
ACHIEVEMENTS = {
    # Logros de Equipo
    'first_blood': AchievementDefinition(
        code='first_blood',
        name='First Blood',
        description='¡Sangre fresca! Sé el primer equipo en resolver cualquier challenge del CTF. La velocidad y la astucia son tu mejor arma.',
        icon='🩸',
        category='team',
        check_func=lambda team, user=None: team.first_bloods.exists()
    ),
    'speed_demon': AchievementDefinition(
        code='speed_demon',
        name='Speed Demon',
        description='Velocidad supersónica. Resuelve un challenge en menos de 5 minutos desde el inicio del CTF. ¿Quién necesita tiempo para pensar?',
        icon='⚡',
        category='team',
        check_func=lambda team, user=None: team.submissions.filter(
            is_correct=True,
            submitted_at__lte=timezone.now() - timedelta(minutes=5)
        ).exists()
    ),
    'night_owl': AchievementDefinition(
        code='night_owl',
        name='Night Owl',
        description='El búho nocturno nunca duerme. Resuelve un challenge entre las 2:00 AM y 6:00 AM. El café es opcional, la dedicación no.',
        icon='🦉',
        category='team',
        check_func=lambda team, user=None: team.submissions.filter(
            is_correct=True,
            submitted_at__hour__gte=2,
            submitted_at__hour__lt=6
        ).exists()
    ),
    'perfectionist': AchievementDefinition(
        code='perfectionist',
        name='Perfectionist',
        description='Perfección absoluta. Resuelve 5 challenges sin un solo intento fallido. Cero errores, solo victorias. ¿Primera vez o simplemente genio?',
        icon='💯',
        category='team',
        check_func=lambda team, user=None: (
            team.submissions.filter(is_correct=True).count() >= 5 and
            team.submissions.filter(is_correct=False).count() == 0
        )
    ),
    'jack_of_all_trades': AchievementDefinition(
        code='jack_of_all_trades',
        name='Jack of All Trades',
        description='Versatilidad máxima. Demuestra tu dominio resolviendo al menos un challenge de cada categoría disponible. Web, crypto, pwn... ¡lo que sea!',
        icon='🎭',
        category='team',
        check_func=lambda team, user=None: check_all_categories(team)
    ),
    'blood_thirsty': AchievementDefinition(
        code='blood_thirsty',
        name='Blood Thirsty',
        description='Sed de sangre insaciable. Consigue 3 o más first bloods. Siempre primeros, siempre hambrientos, siempre dominantes.',
        icon='🔴',
        category='team',
        check_func=lambda team, user=None: team.first_bloods.count() >= 3
    ),
    'unstoppable': AchievementDefinition(
        code='unstoppable',
        name='Unstoppable',
        description='Imparable como un cohete. Resuelve 3 challenges consecutivos en menos de 30 minutos. La velocidad se encuentra con la precisión.',
        icon='🚀',
        category='team',
        check_func=lambda team, user=None: check_solving_streak(team)
    ),
    'half_way': AchievementDefinition(
        code='half_way',
        name='Half Way There',
        description='Punto medio alcanzado. Has resuelto el 50% de todos los challenges disponibles. La meta está más cerca, pero el camino continúa.',
        icon='📊',
        category='team',
        check_func=lambda team, user=None: check_half_challenges(team)
    ),
    'completionist': AchievementDefinition(
        code='completionist',
        name='Completionist',
        description='¡La corona es tuya! Has conquistado TODOS los challenges del CTF. Nada se interpone en tu camino. Leyenda absoluta.',
        icon='👑',
        category='team',
        check_func=lambda team, user=None: check_all_challenges(team)
    ),
    'comeback_kid': AchievementDefinition(
        code='comeback_kid',
        name='Comeback Kid',
        description='¡El regreso épico! Escala 5 posiciones o más en el ranking del CTF. Nunca subestimes a un equipo decidido.',
        icon='📈',
        category='team',
        check_func=lambda team, user=None: False  # Se verifica manualmente en views
    ),
    
    # Logros Individuales
    'solo_warrior': AchievementDefinition(
        code='solo_warrior',
        name='Solo Warrior',
        description='Guerrero solitario. Resuelve 10 challenges personalmente. Tu equipo te necesita, pero tú solo te necesitas a ti mismo.',
        icon='⚔️',
        category='individual',
        check_func=lambda team, user: user.submissions.filter(is_correct=True).count() >= 10
    ),
    'early_bird': AchievementDefinition(
        code='early_bird',
        name='Early Bird',
        description='El madrugador captura el gusano. Sé el primer jugador en resolver cualquier challenge. Primera sangre, gloria individual.',
        icon='🐦',
        category='individual',
        check_func=lambda team, user: user.first_bloods.exists()
    ),
    'persistent': AchievementDefinition(
        code='persistent',
        name='Persistent',
        description='La persistencia vence la resistencia. Resuelve un challenge después de 10 intentos fallidos. Nunca te rindas, nunca te detengas.',
        icon='💪',
        category='individual',
        check_func=lambda team, user: check_persistence(user)
    ),
    'sharpshooter': AchievementDefinition(
        code='sharpshooter',
        name='Sharpshooter',
        description='Precisión quirúrgica. Resuelve 3 challenges con 100% de precisión sin ningún error. Cada disparo cuenta, cada flag es perfecta.',
        icon='🎯',
        category='individual',
        check_func=lambda team, user: check_accuracy(user)
    ),
}

def check_all_categories(team):
    """Verifica si el equipo resolvió challenges de todas las categorías"""
    from challenges.models import Category
    total_categories = Category.objects.count()
    if total_categories == 0:
        return False
    
    solved_categories = team.submissions.filter(
        is_correct=True
    ).values('challenge__category').distinct().count()
    
    return solved_categories >= total_categories

def check_solving_streak(team):
    """Verifica si resolvió 3 challenges seguidos en menos de 30 minutos"""
    submissions = team.submissions.filter(is_correct=True).order_by('submitted_at')[:3]
    
    if submissions.count() < 3:
        return False
    
    first = submissions[0].submitted_at
    third = submissions[2].submitted_at
    
    return (third - first).total_seconds() <= 1800  # 30 minutos

def check_half_challenges(team):
    """Verifica si resolvió al menos el 50% de los challenges"""
    from challenges.models import Challenge
    total_challenges = Challenge.objects.count()
    if total_challenges == 0:
        return False
    
    solved = team.submissions.filter(is_correct=True).values('challenge').distinct().count()
    return solved >= (total_challenges / 2)

def check_all_challenges(team):
    """Verifica si resolvió todos los challenges"""
    from challenges.models import Challenge
    total_challenges = Challenge.objects.count()
    if total_challenges == 0:
        return False
    
    solved = team.submissions.filter(is_correct=True).values('challenge').distinct().count()
    return solved >= total_challenges

def check_persistence(user):
    """Verifica si resolvió después de 10 intentos fallidos"""
    from challenges.models import Submission
    
    # Buscar challenges donde tuvo 10+ fallos antes de acertar
    user_challenges = user.submissions.values('challenge').distinct()
    
    for challenge_dict in user_challenges:
        challenge_id = challenge_dict['challenge']
        submissions = user.submissions.filter(
            challenge_id=challenge_id
        ).order_by('submitted_at')
        
        failed_count = 0
        for sub in submissions:
            if not sub.is_correct:
                failed_count += 1
            else:
                if failed_count >= 10:
                    return True
                break
    
    return False

def check_accuracy(user):
    """Verifica si tiene 3 challenges resueltos sin errores"""
    from challenges.models import Submission
    
    # Obtener challenges resueltos
    solved_challenges = user.submissions.filter(is_correct=True).values_list('challenge_id', flat=True)
    
    perfect_count = 0
    for challenge_id in solved_challenges:
        # Verificar si solo tiene 1 submission (la correcta) para este challenge
        total_attempts = user.submissions.filter(challenge_id=challenge_id).count()
        if total_attempts == 1:
            perfect_count += 1
            if perfect_count >= 3:
                return True
    
    return False

def check_achievements(team, user=None):
    """
    Verifica qué logros ha conseguido un equipo o usuario
    Retorna una lista de códigos de logros conseguidos
    """
    earned = []
    
    for code, achievement in ACHIEVEMENTS.items():
        try:
            if achievement.check_func(team, user):
                earned.append(code)
        except Exception as e:
            # Si hay error en la verificación, simplemente no otorgar el logro
            print(f"Error checking achievement {code}: {e}")
            continue
    
    return earned

def get_achievement_info(code):
    """Obtiene la información de un logro por su código"""
    return ACHIEVEMENTS.get(code)
