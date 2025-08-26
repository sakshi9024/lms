from django.db import models
from base.choices import LEVEL_TYPE_CHOICES, GENDER_CHOICES,STATUS_CHOICES, LOCATION_CHOICES

# Create your models here.

class Common(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class Department(Common):
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=500)
    
    def __str__(self):
        return self.name

 
class Role(Common):
    title = models.CharField(max_length=200)
    level_type = models.CharField(max_length=200,choices=LEVEL_TYPE_CHOICES)
    description = models.TextField(max_length=500)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    entry_time = models.TimeField()
    exit_time = models.TimeField()
    
    def __str__(self):
        return f"{self.level_type} {self.title}"

class Employee(Common):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    address = models.TextField(max_length=250)
    joining_date = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employeedepartment')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='emprole')
    manager = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.role.title} ({self.department.name})"


class Attendance(Common):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    attendance_type = models.CharField(max_length=50, choices=LOCATION_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True, blank=True)
    late_check_in = models.BooleanField(default=False)
    early_check_out = models.BooleanField(default=False)    
    
    def __str__(self):
        return f"{self.employee.first_name} ({self.date})"



