from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('', 'Не выбрана'),
        ('broker', 'Брокер'),
        ('agent', 'Агент'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile', verbose_name='Пользователь')
    last_name = models.CharField(max_length=100, blank=True, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, blank=True, verbose_name='Имя')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, verbose_name='Роль')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    subject = models.CharField(max_length=200, verbose_name="Тема")
    message = models.TextField(verbose_name="Предложение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.subject[:50]}"


class Deal(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('closed', 'Закрыта'),
        ('cancelled', 'Отменена'),
    ]
    title = models.CharField(max_length=200, verbose_name='Название сделки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Сумма (₽)')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='deals', verbose_name='Ответственный'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата закрытия')
    notes = models.TextField(blank=True, verbose_name='Примечания')

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.get_status_display()}]'


class OsagoPolicy(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Черновик'),
        ('active',    'Активен'),
        ('expired',   'Истёк'),
        ('cancelled', 'Аннулирован'),
    ]
    VEHICLE_CATEGORY_CHOICES = [
        ('B',  'B — легковые, мотоциклы'),
        ('C',  'C — грузовые'),
        ('D',  'D — автобусы'),
        ('E',  'E — прицепы'),
        ('Tb', 'Tb — троллейбусы'),
        ('Tm', 'Tm — трамваи'),
    ]
    DRIVERS_CHOICES = [
        ('limited',   'Ограниченный список'),
        ('unlimited', 'Без ограничений'),
    ]

    # Общие
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='osago_policies', verbose_name='Создал'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    # Страхователь
    insured_last_name  = models.CharField(max_length=100, blank=True, verbose_name='Фамилия страхователя')
    insured_first_name = models.CharField(max_length=100, blank=True, verbose_name='Имя страхователя')
    insured_middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество страхователя')
    insured_dob        = models.DateField(null=True, blank=True, verbose_name='Дата рождения страхователя')
    insured_phone      = models.CharField(max_length=20, blank=True, verbose_name='Телефон страхователя')
    insured_email      = models.EmailField(blank=True, verbose_name='Email страхователя')

    # Транспортное средство
    vehicle_make     = models.CharField(max_length=100, blank=True, verbose_name='Марка ТС')
    vehicle_model    = models.CharField(max_length=100, blank=True, verbose_name='Модель ТС')
    vehicle_year     = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Год выпуска')
    vehicle_vin      = models.CharField(max_length=20, blank=True, verbose_name='VIN')
    vehicle_plate    = models.CharField(max_length=20, blank=True, verbose_name='Гос. номер')
    vehicle_category = models.CharField(max_length=5, choices=VEHICLE_CATEGORY_CHOICES, default='B', verbose_name='Категория ТС')
    engine_power     = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Мощность двигателя (л.с.)')

    # Полис
    drivers_type   = models.CharField(max_length=20, choices=DRIVERS_CHOICES, default='limited', verbose_name='Список водителей')
    policy_start   = models.DateField(null=True, blank=True, verbose_name='Дата начала')
    policy_end     = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    insurer_name   = models.CharField(max_length=200, blank=True, verbose_name='Страховая компания')
    premium_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Страховая премия (₽)')
    policy_number  = models.CharField(max_length=50, blank=True, verbose_name='Номер полиса')
    notes          = models.TextField(blank=True, verbose_name='Примечания')

    class Meta:
        verbose_name = 'Полис ОСАГО'
        verbose_name_plural = 'Полисы ОСАГО'
        ordering = ['-created_at']

    def __str__(self):
        fio = ' '.join(filter(None, [self.insured_last_name, self.insured_first_name]))
        plate = self.vehicle_plate or 'б/н'
        return f'ОСАГО {plate} — {fio or "без страхователя"} [{self.get_status_display()}]'
