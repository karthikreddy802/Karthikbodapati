import re
import pdfplumber
from pyexpat.errors import messages
import random
import string
import os
import uuid
import qrcode
from datetime import datetime
from io import BytesIO
from django.shortcuts import render, redirect,get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db.models import Avg, Max
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Exam, Question
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from .models import Exam,Question,ExamSession,Result,User,Attempt


from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ---------------------------
# RANDOM GENERATORS
# ---------------------------

def generate_username():
    return "exam_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "@#$", k=8))

# ---------------------------
# REGISTER
# ---------------------------



def register_view(request):
    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        #  username already exists check
        #if User.objects.filter(username=username).exists():

        #  email validation
        try:
            validate_email(email)
        except ValidationError:
            return render(request, "myapp/register.html", {
                "error": "Enter valid email"
            })

        password = generate_password()

        # create user safely
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        # send email
        send_mail(
            subject="Online Exam Login Details",
            message=f"""
Welcome to Online Exam Portal

Username: {username}
Email: {email}
Password: {password}

Login:
http://127.0.0.1:8000/user_login/
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('user_login')

    return render(request, "myapp/register.html")
# ---------------------------
# USER LOGIN
# ---------------------------


def user_login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        # Get latest account for that email
        user = User.objects.filter(email=email).order_by('-id').first()

        if user and check_password(password, user.password):
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['user_logged_in'] = True
            return redirect('instructions')
        else:
            return render(request, "myapp/user_login.html", {
                "error": "Invalid Email or Password"
            })

    return render(request, "myapp/user_login.html")


# ---------------------------
# INSTRUCTIONS
# ---------------------------

def instructions_view(request):
    if not request.session.get("user_logged_in"):
        return redirect("user_login")

    exams = Exam.objects.all()

    return render(request, "myapp/instructions.html", {
        "exams": exams
    })

# ---------------------------
# MULTI EXAM VIEW
# ---------------------------

def exam_view(request, exam_id):

    if not request.session.get("user_logged_in"):
        return redirect("user_login")

    exam = get_object_or_404(Exam, id=exam_id)

    # get questions
    questions = list(Question.objects.filter(exam=exam))
    random.shuffle(questions)

    # save question ids in session
    request.session["exam_q_ids"] = [q.id for q in questions]

    return render(request, "myapp/exam.html", {
        "exam": exam,
        "questions": questions,
        "remaining_time": 1800
    })



# ---------------------------
# FINISH
# ---------------------------

def exam_finished_view(request):
    return render(request,"myapp/exam_finished.html",{
        "correct":request.session.get("correct",0),
        "wrong":request.session.get("wrong",0),
        "answered":request.session.get("answered",0),
        "unanswered":request.session.get("unanswered",0),
        "total":request.session.get("total",0),
        "percentage":request.session.get("percentage",0),
        "status":request.session.get("status","FAIL"),
    })


def update_violation(request):

    session_id = request.POST.get("session_id")
    vtype = request.POST.get("type")

    s = ExamSession.objects.get(id=session_id)

    if vtype=="tab":
        s.tab_switches += 0
    if vtype=="face":
        s.face_warnings += 0

    if s.tab_switches>=0 or s.face_warnings>=1:
        s.is_cheated=True

    s.save()
    return JsonResponse({"ok":True})

# ---------------------------
# ADMIN
# ---------------------------

def admin_login_view(request):
    if request.method == "POST":
        if request.POST.get("username")=="admin" and request.POST.get("password")=="admin123":
            request.session["admin_logged_in"]=True
            return redirect("admin_panel")
    return render(request,"myapp/admin_login.html")



def admin_panel_view(request):

    # ================= BASIC COUNTS =================
    total_students = User.objects.count()
    total_exams = Exam.objects.count()
    total_attempts = Result.objects.count()

    # ================= AVERAGE SCORE =================
    avg_score = Result.objects.aggregate(avg=Avg("percentage"))["avg"]
    if avg_score is None:
        avg_score = 0

    # ================= PASS RATE =================
    passed = Result.objects.filter(percentage__gte=40).count()
    pass_rate = 0
    if total_attempts > 0:
        pass_rate = round((passed / total_attempts) * 100, 2)

    # ================= TOP SCORER =================
    top_result = Result.objects.order_by("-percentage").first()
    top_scorer = None
    if top_result:
        top_scorer = f"{top_result.username} ({top_result.percentage}%)"

    # ================= RESULTS TABLE =================
    results = Result.objects.select_related("exam").order_by("-submitted_at")

    # ================= EXAMS =================
    exams = Exam.objects.all()

    context = {
        "total_students": total_students,
        "total_exams": total_exams,
        "total_attempts": total_attempts,
        "avg_score": round(avg_score, 2),
        "pass_rate": pass_rate,
        "top_scorer": top_scorer,
        "exams": exams,
        "results": results,
    }

    results = Result.objects.select_related("exam").order_by("-submitted_at")
    return render(request, "myapp/admin_panel.html", context)



def home_view(request):
    exams = Exam.objects.all()
    return render(request, "myapp/home.html", {"exams": exams})

def contact_view(request):
    return render(request,"myapp/contact.html")

def about_view(request):
    return render(request,"myapp/about.html")

def login_view(request):
    return render(request,"myapp/login.html")



def add_exam_view(request):
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        Exam.objects.create(
            title=title,
            description=description
        )

        return redirect("admin_panel")

    return render(request, "myapp/add_exam.html")


def view_exam_view(request):
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    # Logic to fetch exams (not implemented)
    exams = []
    return render(request,"myapp/view_exam.html",{"exams":exams})

def delete_exam_view(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    exam.delete()
    return redirect('admin_panel')


def update_exam_view(request, exam_id):
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    if request.method == "POST":
        # Logic to update exam (not implemented)
        return redirect("view_exam")

    # Logic to fetch exam details (not implemented)
    exam = {}
    return render(request,"myapp/update_exam.html",{"exam":exam})

def add_question_view(request, exam_id):
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    exam = Exam.objects.get(id=exam_id)

    if request.method == "POST":
        Question.objects.create(
            exam=exam,
            text=request.POST.get("text"),
            option1=request.POST.get("option1"),
            option2=request.POST.get("option2"),
            option3=request.POST.get("option3"),
            option4=request.POST.get("option4"),
            correct_answer=request.POST.get("correct_answer"),
        )
        return redirect("admin_panel")

    return render(
        request,
        "myapp/add_question.html",
        {"exam": exam}
    )

def generate_certificate_view(request):

    if not request.session.get('user_id'):
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    # GET LATEST RESULT
    result = Result.objects.filter(
        email=user.email
    ).order_by('-submitted_at').first()

    if not result:
        return HttpResponse("No exam data found.")

    # 🔥 GET NAME FROM RESULT TABLE
    username = result.username if result.username else user.username

    score = result.score
    total = result.total
    percentage = round(result.percentage, 2)

    if percentage < 40:
        return HttpResponse("Sorry! You did not pass the exam.")

    certificate_id = result.certificate_id

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="SSSIT_Certificate.pdf"'

    width, height = landscape(A4)
    c = canvas.Canvas(response, pagesize=landscape(A4))
    center_x = width / 2

    # Background
    c.setFillColor(colors.whitesmoke)
    c.rect(0, 0, width, height, fill=1)

    # Watermark
    c.saveState()
    c.setFont("Helvetica-Bold", 70)
    c.setFillColorRGB(0.90, 0.90, 0.90)
    c.translate(width / 2, height / 2)
    c.rotate(45)

    for x in range(-2000, 2000, 350):
        for y in range(-1500, 1500, 300):
            c.drawCentredString(x, y, "SSSIT")

    c.restoreState()

    # Borders
    c.setStrokeColor(colors.HexColor("#C9A227"))
    c.setLineWidth(6)
    c.rect(35, 35, width-70, height-70)

    c.setStrokeColor(colors.HexColor("#0B3D91"))
    c.setLineWidth(2)
    c.rect(50, 50, width-100, height-100)

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#0B3D91"))
    c.drawCentredString(center_x, height-90, "SSSIT INSTITUTE OF TECHNOLOGY")

    c.setFont("Helvetica-Bold", 38)
    c.setFillColor(colors.black)
    c.drawCentredString(center_x, height-150, "CERTIFICATE OF COMPLETION")

    c.line(center_x-200, height-165, center_x+200, height-165)

    # Text
    c.setFont("Helvetica", 22)
    c.drawCentredString(center_x, height-210,
        "This certificate is proudly presented to")

    # ✅ CORRECT NAME PRINT
    c.setFont("Helvetica-Bold", 42)
    c.setFillColor(colors.HexColor("#1A237E"))
    c.drawCentredString(center_x, height-260, username.upper())

    c.setFont("Helvetica", 20)
    c.setFillColor(colors.black)
    c.drawCentredString(
        center_x,
        height-310,
        f"for successfully completing the {result.exam.title} Examination"
    )

    c.drawCentredString(
        center_x,
        height-340,
        f"with an outstanding score of {score}/{total} ({percentage}%)"
    )

    today = datetime.today().strftime("%d %B %Y")
    c.setFont("Helvetica", 14)
    c.drawString(90, 110, f"Issued On: {today}")
    c.drawString(90, 90, f"Certificate ID: {certificate_id}")

    # Signature
    sign_path = os.path.join(settings.BASE_DIR, "myapp", "media", "images", "signature_1.png")
    if os.path.exists(sign_path):
        c.drawImage(sign_path, width-330, 120, 180, 60, mask='auto')

    c.line(width-350, 110, width-150, 110)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width-250, 95, "Authorized Signatory")

    # QR
    verify_url = f"http://127.0.0.1:8000/verify/{certificate_id}/"
    qr_img = qrcode.make(verify_url)

    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_image = ImageReader(buffer)

    c.drawImage(qr_image, center_x-40, 100, 80, 80)
    c.setFont("Helvetica", 10)
    c.drawCentredString(center_x, 90, "Scan to Verify")

    c.save()
    return response

import pdfplumber
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Exam, Question


def upload_pdf_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf_file")
        if not pdf_file:
            return render(request, "myapp/upload_pdf.html", {
                "exam": exam,
                "error": "Upload PDF"
            })
        # save PDF
        exam.pdf_file = pdf_file
        exam.save()
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        blocks = re.split(r"Q\d+\.", text)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            try:
                lines = [l.strip() for l in block.split("\n") if l.strip()]
                if len(lines) < 6:
                    continue
                question_text = lines[0]
                option1 = lines[1].replace("A.", "")
                option2 = lines[2].replace("B.", "")
                option3 = lines[3].replace("C.", "")
                option4 = lines[4].replace("D.", "")
                answer_line = [l for l in lines if "Answer" in l][0]
                correct = answer_line.split(":")[-1].strip()
                Question.objects.create(
                    exam=exam,
                    text=question_text,
                    option1=option1,
                    option2=option2,
                    option3=option3,
                    option4=option4,
                    correct_answer=correct
                )
            except:
                continue
        messages.success(request, "PDF uploaded & questions imported")
        return redirect("admin_panel")
    return render(request, "myapp/upload_pdf.html", {"exam": exam})


def start_exam(request, exam_id):

    if not request.session.get("user_logged_in"):
        return redirect("user_login")

    user = User.objects.get(id=request.session["user_id"])
    exam = Exam.objects.get(id=exam_id)

    qs = list(Question.objects.filter(exam=exam))
    random.shuffle(qs)
    qs = qs[:25]

    request.session["exam_q_ids"] = [q.id for q in qs]

    for q in qs:
        Attempt.objects.update_or_create(
            email=user.email,
            exam=exam,
            question=q,
            defaults={
                "username": user.username,
                "selected_option": ""
            }
        )

    return render(request, "myapp/exam.html", {
        "exam": exam,
        "questions": qs,
        "remaining_time": 1800
    })

def convert_pdf_to_exam(request, exam_id):

    exam = get_object_or_404(Exam, id=exam_id)
    if not exam.pdf_file:
        return redirect("admin_panel")
    text = ""
    with pdfplumber.open(exam.pdf_file.path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    # split questions by number
    blocks = re.split(r"\n\d+\.", text)
    count = 0
    for b in blocks:
        lines = [l.strip() for l in b.split("\n") if l.strip()]
        if len(lines) < 5:
            continue
        try:
            q = lines[0]
            opt1 = re.sub(r"^[A-Da-d][\.\)]\s*", "", lines[1])
            opt2 = re.sub(r"^[A-Da-d][\.\)]\s*", "", lines[2])
            opt3 = re.sub(r"^[A-Da-d][\.\)]\s*", "", lines[3])
            opt4 = re.sub(r"^[A-Da-d][\.\)]\s*", "", lines[4])
            answer_line = [l for l in lines if "ans" in l.lower()]
            if not answer_line:
                continue
            correct = answer_line[0].split(":")[-1].strip()[0].upper()
            Question.objects.create(
                exam=exam,
                text=q,
                option1=opt1,
                option2=opt2,
                option3=opt3,
                option4=opt4,
                correct_answer=correct
            )

            count += 1

        except:
            continue

    print("Questions added:", count)
    return redirect("admin_panel")
def submit_exam_view(request, exam_id):

    if not request.session.get("user_logged_in"):
        return redirect("user_login")

    user = User.objects.get(id=request.session["user_id"])
    exam = get_object_or_404(Exam, id=exam_id)

    # ALWAYS use name from register page
    username = user.username

    # QUESTIONS
    q_ids = request.session.get("exam_q_ids")

    if q_ids:
        questions = Question.objects.filter(id__in=q_ids)
    else:
        questions = Question.objects.filter(exam=exam)

    correct = 0
    wrong = 0
    answered = 0
    total = questions.count()

    for q in questions:
        selected = request.POST.get(str(q.id))

        if selected:
            answered += 1

            if selected == q.correct_answer:
                correct += 1
            else:
                wrong += 1

    percentage = (correct / total) * 100 if total > 0 else 0
    status = "PASS" if percentage >= 40 else "FAIL"

    #  SAVE RESULT WITH REGISTER NAME
    result = Result.objects.create(
        username=username,
        email=user.email,
        exam=exam,
        score=correct,
        total=total,
        percentage=percentage,
        certificate_id="CERT-" + str(uuid.uuid4())[:8].upper()
    )

    # SAVE RESULT ID FOR CERTIFICATE
    request.session["result_id"] = result.id

    # SESSION DATA
    request.session["correct"] = correct
    request.session["wrong"] = wrong
    request.session["answered"] = answered
    request.session["unanswered"] = total - answered
    request.session["total"] = total
    request.session["percentage"] = percentage
    request.session["status"] = status

    return redirect("exam_finished")
def admin_logout_view(request):
        request.session.flush()
        return render(request,"myapp/admin_logout.html")


def verify_certificate_view(request, certificate_id):
    certificate_id = certificate_id.replace("CERT-", "")
    result = Result.objects.get(certificate_id=certificate_id)
    return render(request, "myapp/verify_certificate.html", {"result": result})





