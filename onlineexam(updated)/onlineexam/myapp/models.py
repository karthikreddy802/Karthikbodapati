from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.email


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    pdf_file = models.FileField(upload_to='exam_pdfs/', null=True, blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)

    def __str__(self):
        return self.text
    
class Result(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    percentage = models.FloatField()
    certificate_id = models.CharField(max_length=50, unique=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class Attempt(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=200, null=True, blank=True)

class ExamSession(models.Model):
    email = models.EmailField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    tab_switches = models.IntegerField(default=0)
    face_warnings = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    is_cheated = models.BooleanField(default=False)

