from django.db import models


class Asset(models.Model):
    STATUS_CHOICES = ("in_work", "broken", "under_repair", "in_reserve")
    STATUS_CHOICES_RUS = ("В работе", "Сломано", "В ремонте", "В запасе")
    STATUS_CHOICES = list(zip(STATUS_CHOICES, STATUS_CHOICES_RUS))

    name = models.CharField(max_length=256, verbose_name='Наименование')
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    location = models.ForeignKey("Location", on_delete=models.CASCADE, verbose_name=" Местоположение")
    year_of_purchase = models.DateField(verbose_name="Дата покупки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата и время обновления")
    price = models.DecimalField(verbose_name="Стоимость")
    state = models.IntegerField(verbose_name="Состояние", choices=[1, 2, 3, 4, 5])
    status = models.CharField(max_length=256, verbose_name='Статус', choices=STATUS_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Актив"
        verbose_name_plural = "Активвы"


class AssetImage(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Изображение", related_name="images")
    image = models.ImageField(upload_to="images", verbose_name="Изображенеие")

    def __str__(self):
        return self.asset.name

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


class Location:
    name = models.CharField(max_length=256, verbose_name='Название')
    city = models.CharField(max_length=256, verbose_name='Город')
    address = models.CharField(max_length=256, verbose_name='Адрес')
    description = models.TextField(verbose_name="Описание", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class Order(models.Model):
    file = models.FileField(upload_to="files", verbose_name="Файл")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")

    def __str__(self):
        return self.created_at

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"
