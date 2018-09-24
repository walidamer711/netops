from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Projects(models.Model):
    project_name = models.CharField(max_length=100)

    def __str__(self):
        return self.project_name

    def get_tasks_count(self):
        return Tasks.objects.filter(project=self).count()


class Tasks(models.Model):
    task = models.CharField(max_length=1000)
    status = models.TextField(max_length=4000)
    is_completed = models.BooleanField(default=False)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, default=1, on_delete=models.CASCADE)


    def __str__(self):
        return '%s %s' % (self.task, self.project)
