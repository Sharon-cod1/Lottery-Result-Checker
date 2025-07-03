from django.db import models
from django.core.validators import RegexValidator

class LotteryDraw(models.Model):
    draw_name = models.CharField(max_length=50)
    draw_date = models.DateField()
    draw_time = models.TimeField()
    result_pdf = models.FileField(upload_to='lottery_results/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.draw_name} - {self.draw_date}"

class Prize(models.Model):
    PRIZE_TYPES = [
        ('1st', '1st Prize'),
        ('2nd', '2nd Prize'),
        ('3rd', '3rd Prize'),
        ('cons', 'Consolation Prize'),
        ('4th', '4th Prize'),
        ('5th', '5th Prize'),
        ('6th', '6th Prize'),
        ('7th', '7th Prize'),
        ('8th', '8th Prize'),
        ('9th', '9th Prize'),
    ]
    
    lottery_draw = models.ForeignKey(LotteryDraw, on_delete=models.CASCADE)
    prize_type = models.CharField(max_length=10, choices=PRIZE_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    ticket_code = models.CharField(max_length=8, validators=[
        RegexValidator(
            regex='^[A-Z]{2}\d{6}$',
            message='Ticket code must be 2 letters followed by 6 digits'
        )
    ])
    location = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_prize_type_display()} - {self.ticket_code}"