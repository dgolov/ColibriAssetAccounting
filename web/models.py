from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    city = models.CharField(max_length=256, verbose_name='Город', blank=True, null=True)
    address = models.CharField(max_length=256, verbose_name='Адрес', blank=True, null=True)
    phone = models.CharField(max_length=32, verbose_name="Номер телефона", blank=True, null=True)
    description = models.TextField(verbose_name="Описание", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class Asset(models.Model):
    STATUS_CHOICES = ("in_work", "broken", "under_repair", "in_reserve")
    STATUS_CHOICES_RUS = ("В работе", "Сломано", "В ремонте", "В запасе")
    STATUS_CHOICES = list(zip(STATUS_CHOICES, STATUS_CHOICES_RUS))

    STATE_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))

    name = models.CharField(max_length=256, verbose_name='Наименование')
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        verbose_name="Местоположение",
        related_name='assets'
    )
    year_of_purchase = models.DateField(verbose_name="Дата покупки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата и время обновления")
    price = models.DecimalField(verbose_name="Стоимость", decimal_places=2, max_digits=7)
    state = models.IntegerField(verbose_name="Состояние", choices=STATE_CHOICES)
    status = models.CharField(max_length=256, verbose_name='Статус', choices=STATUS_CHOICES)
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    auto_update_price = models.BooleanField(default=False, verbose_name="Автообновление стоимости")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Актив"
        verbose_name_plural = "Активы"


class AssetImage(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Актив", related_name="images")
    image = models.ImageField(upload_to="images", verbose_name="Изображенеие")

    def __str__(self):
        return self.asset.name

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


class Order(models.Model):
    file = models.FileField(upload_to="files", verbose_name="Файл")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")

    def __str__(self):
        return self.created_at

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"


class History(models.Model):
    STATUS_CHOICES = ("in_work", "broken", "under_repair", "in_reserve")
    STATUS_CHOICES_RUS = ("В работе", "Сломано", "В ремонте", "В запасе")
    STATUS_CHOICES = list(zip(STATUS_CHOICES, STATUS_CHOICES_RUS))

    STATE_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))

    event_name = models.TextField(verbose_name='Наименование события')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Актив", related_name="history")
    old_location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        verbose_name="Местоположение",
        blank=True,
        null=True,
        related_name='old_history'
    )
    new_location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        verbose_name="Местоположение",
        blank=True,
        null=True,
        related_name='new_history'
    )
    old_price = models.DecimalField(verbose_name="Стоимость", decimal_places=2, max_digits=7, blank=True, null=True)
    new_price = models.DecimalField(verbose_name="Стоимость", decimal_places=2, max_digits=7, blank=True, null=True)
    old_state = models.IntegerField(verbose_name="Состояние", choices=STATE_CHOICES, blank=True, null=True)
    new_state = models.IntegerField(verbose_name="Состояние", choices=STATE_CHOICES, blank=True, null=True)
    old_status = models.CharField(max_length=256, verbose_name='Статус', choices=STATUS_CHOICES, blank=True, null=True)
    new_status = models.CharField(max_length=256, verbose_name='Статус', choices=STATUS_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")

    def __str__(self):
        return f"{self.created_at} - {self.asset.name}"

    class Meta:
        verbose_name = "История"
        verbose_name_plural = "История"
