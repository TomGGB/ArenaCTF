"""
Script para inicializar datos de ejemplo en la plataforma CTF
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from teams.models import Team
from challenges.models import Category, Challenge

class Command(BaseCommand):
    help = 'Inicializa datos de ejemplo para la plataforma CTF'

    def handle(self, *args, **kwargs):
        self.stdout.write('🎮 Inicializando datos de ejemplo...\n')

        # Crear categorías
        categories_data = [
            {'name': 'Web', 'icon': '🌐', 'color': '#00ff41'},
            {'name': 'Crypto', 'icon': '🔐', 'color': '#ff00ff'},
            {'name': 'Forensics', 'icon': '🔍', 'color': '#00ffff'},
            {'name': 'Reversing', 'icon': '⚙️', 'color': '#ffff00'},
            {'name': 'Pwn', 'icon': '💥', 'color': '#ff0000'},
            {'name': 'Misc', 'icon': '🎲', 'color': '#ffa500'},
        ]

        self.stdout.write('📁 Creando categorías...')
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            if created:
                self.stdout.write(f'  ✓ Categoría creada: {category.name}')

        # Crear challenges de ejemplo
        challenges_data = [
            {
                'title': 'SQL Injection Básico',
                'description': 'Encuentra la forma de bypassear el login usando SQL injection.',
                'category': 'Web',
                'points': 100,
                'flag': 'flag{sql_1nj3ct10n_1s_3asy}',
                'hints': 'Prueba con comillas simples en el campo de usuario.'
            },
            {
                'title': 'XSS Reflected',
                'description': 'Inyecta código JavaScript en la página vulnerable.',
                'category': 'Web',
                'points': 150,
                'flag': 'flag{xss_r3fl3ct3d_att4ck}',
                'hints': 'Los filtros son tu enemigo, encuentra la forma de bypassearlos.'
            },
            {
                'title': 'Caesar Cipher',
                'description': 'Descifra el siguiente mensaje: Synt{pe3cn_vf_gbb_3nfl}',
                'category': 'Crypto',
                'points': 50,
                'flag': 'flag{cr3pt0_is_too_3asy}',
                'hints': 'Es un cifrado por sustitución clásico.'
            },
            {
                'title': 'RSA Baby',
                'description': 'n=8218, e=17. Cifrado: 5234. ¿Cuál es el mensaje?',
                'category': 'Crypto',
                'points': 200,
                'flag': 'flag{rs4_b4by_ch4ll3ng3}',
                'hints': 'Los números son pequeños, puedes factorizar n fácilmente.'
            },
            {
                'title': 'Hidden in Plain Sight',
                'description': 'Analiza la imagen adjunta. La flag está escondida.',
                'category': 'Forensics',
                'points': 100,
                'flag': 'flag{st3g4n0gr4phy_1s_c00l}',
                'hints': 'Usa herramientas como strings o exiftool.'
            },
            {
                'title': 'Memory Dump',
                'description': 'Analiza el volcado de memoria y encuentra la contraseña.',
                'category': 'Forensics',
                'points': 250,
                'flag': 'flag{m3m0ry_f0r3ns1cs}',
                'hints': 'Volatility es tu amigo.'
            },
            {
                'title': 'Crackme Easy',
                'description': 'Reverse engineer el binario y encuentra la flag.',
                'category': 'Reversing',
                'points': 150,
                'flag': 'flag{r3v3rs3_3ng1n33r1ng}',
                'hints': 'Usa herramientas como Ghidra o IDA.'
            },
            {
                'title': 'Buffer Overflow',
                'description': 'Explota el buffer overflow y obtén shell.',
                'category': 'Pwn',
                'points': 300,
                'flag': 'flag{buff3r_0v3rfl0w_pwn3d}',
                'hints': 'Desactiva ASLR y encuentra el offset correcto.'
            },
        ]

        self.stdout.write('\n🎯 Creando challenges...')
        for chall_data in challenges_data:
            category = Category.objects.get(name=chall_data['category'])
            challenge, created = Challenge.objects.get_or_create(
                title=chall_data['title'],
                defaults={
                    'description': chall_data['description'],
                    'category': category,
                    'points': chall_data['points'],
                    'flag': chall_data['flag'],
                    'hints': chall_data['hints'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Challenge creado: {challenge.title} ({challenge.points}pts)')

        self.stdout.write('\n✨ ¡Datos de ejemplo creados exitosamente!')
        self.stdout.write('\n📊 Resumen:')
        self.stdout.write(f'  - Categorías: {Category.objects.count()}')
        self.stdout.write(f'  - Challenges: {Challenge.objects.count()}')
        self.stdout.write('\n🚀 ¡La plataforma está lista para usar!')
