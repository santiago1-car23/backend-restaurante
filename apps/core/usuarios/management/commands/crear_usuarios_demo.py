from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.usuarios.models import Rol, Empleado


class Command(BaseCommand):
    help = "Crea usuarios de ejemplo: mesero y cocinero"

    def handle(self, *args, **options):
        # Asegurar roles básicos
        roles_def = [
            ("admin", "Administrador"),
            ("mesero", "Mesero"),
            ("cajero", "Cajero"),
            ("cocinero", "Cocinero"),
        ]

        for cod, _ in roles_def:
            rol, created = Rol.objects.get_or_create(nombre=cod)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Rol creado: {rol.get_nombre_display()}"))

        # Crear usuario mesero
        mesero_user, created = User.objects.get_or_create(
            username="mesero",
            defaults={
                "first_name": "Mesero",
                "last_name": "Demo",
                "is_staff": False,
            },
        )
        if created:
            mesero_user.set_password("mesero123")
            mesero_user.save()
            self.stdout.write(self.style.SUCCESS("✓ Usuario creado: mesero / mesero123"))
        else:
            self.stdout.write("· Usuario 'mesero' ya existe")

        rol_mesero = Rol.objects.filter(nombre="mesero").first()
        if rol_mesero:
            Empleado.objects.get_or_create(
                user=mesero_user,
                defaults={
                    "rol": rol_mesero,
                    "telefono": "",
                    "direccion": "",
                    "activo": True,
                },
            )

        # Crear usuario cocinero
        cocinero_user, created = User.objects.get_or_create(
            username="cocinero",
            defaults={
                "first_name": "Cocinero",
                "last_name": "Demo",
                "is_staff": False,
            },
        )
        if created:
            cocinero_user.set_password("cocinero123")
            cocinero_user.save()
            self.stdout.write(self.style.SUCCESS("✓ Usuario creado: cocinero / cocinero123"))
        else:
            self.stdout.write("· Usuario 'cocinero' ya existe")

        rol_cocinero = Rol.objects.filter(nombre="cocinero").first()
        if rol_cocinero:
            Empleado.objects.get_or_create(
                user=cocinero_user,
                defaults={
                    "rol": rol_cocinero,
                    "telefono": "",
                    "direccion": "",
                    "activo": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("\n✅ Usuarios demo creados/verificados"))
