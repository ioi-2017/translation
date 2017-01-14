from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
import markdown,pdfkit
import codecs
# Create your views here.
class Home(View):
    def get(self, request, *args, **kwargs):
        print('i am here')
        task = Task.objects.all()
        print(task)
        translations = []
        for item in task:
            translations.append((item.id, item.title))

        print(translations)
        return render(request, 'questions.html', context={'translations': translations})


class Questions(View):
    def get(self,request,id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        try:
            trans = Translation.objects.get(user=user, task = task)
        except:
            trans = Translation.objects.create(user= user, task = task, language = user.language)

        if user.rtl == True:
            return render(request,'editor.html', context={'trans' : trans.text , 'task' : task.text , 'quesId':id})
        else :
            return render(request,'editor-eng.html', context={'trans' : trans.text , 'task' : task.text , 'quesId':id})

class SaveQuestion(View):
    def post(self,request):
        user = User.objects.get(username=request.user)
        id = request.POST['id']
        content = request.POST['content']
        print(len(content))
        task = Task.objects.get(id=id)
        try:
            ques = Translation.objects.get(user=user,task=task)
            ques.text = content
            ques.save()
        except:
            ques = Translation.objects.create(user = user, task = task, text=content)
            ques.save()
        print('before retrieve')
        print(len(ques.text))
        print('after retrieve')

        q = Translation.objects.get(user=user,task=task)
        print(len(q.text))
        print('in save question')
        version = Version.objects.create(translation=ques, text=content, date_time = datetime.datetime.now() )
        version.save()
        VersionParticle.objects.filter(translation=ques).delete()
        return HttpResponse("done")


class FirstPage(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(to=reverse('task'))

        if request.user.is_authenticated():
            return redirect(to=reverse('home'))
        else:
            return render(request, 'home.html')

class Login(View):
    def post(self, request):
        username = request.POST.get('mail')
        password = request.POST.get('password')
        # @milad you should probably verify this, it's supposed to login the user
        print("imm heeerreee")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(to=reverse('firstpage'))

        return render(request, 'home.html', {'login_error': True})


class Setting(View):
    def post(self, request):
        print (request.user.username)
        user = User.objects.get(username=request.user.username)
        if (request.POST.get('rtl') == 'on'):
            user.rtl = True
        else:
            user.rtl = False
        user.save()
        return redirect(to=reverse('home'))


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(request=request, to=reverse('firstpage'))

class Tasks(View):
    def get(self,request):
        print('i am here')
        ques = Task.objects.all()
        questions = []
        for item in ques:
            questions.append((item.id, item.title))
        return render(request, 'tasks.html', context={'questions': questions})

    def post(self,request):
        task = Task.objects.create(text = 'Write Your Question',title = 'Task')
        task.save()
        return redirect(to=reverse('task'))

class EditTask(View):
    def get(self,request,id):
        print('in edit task')
        task = Task.objects.get(id=id)
        print(task.text)
        return render(request,'editor-task.html', context={'task' : task.text , 'taskId':id})

class SaveTask(View):
    def post(self,request):
        id = request.POST['id']
        content = request.POST['content']
        task = Task.objects.get(id=id)
        task.text = content
        task.save()
        return HttpResponse("done")


class GeneratePDf(View):
    def post(self,request):
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
        }
        output_file = 'mypdf.pdf'
        print(request.POST['isAdmin'])
        if request.POST['isAdmin'] == 'Yes':
            id = request.POST['TaskId']
            task = Task.objects.get(id=int(id))
            html_text = markdown.markdown(task.text, output_format ='html4',)
            pdfkit.from_string(html_text, output_file)

        else:
            id = request.POST['quesId']
            print(id)
            user = User.objects.get(username = request.user.username)
            translation = Translation.objects.get(user=user, id=id)
            html_text = markdown.markdown(translation.text, output_format = 'html4')
            print(html_text)
            pdfkit.from_string(html_text, output_file, options=options)

        file = open(output_file, 'rb')
        response = HttpResponse(file, content_type='application/pdf')
        response['Content   -Disposition'] = 'inline;filename=some_file.pdf'

        return response

class Versions(View):
    def get(self,request,id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        try:
            trans = Translation.objects.get(user=user, task = task)
        except:
            trans = Translation.objects.create(user= user, task = task, language = user.language, )

        v = []
        vp = []
        versions = Version.objects.filter(translation=trans).order_by('date_time')
        versionParticles = VersionParticle.objects.filter(translation=trans).order_by('date_time')
        for item in versionParticles:
            vp.append((item.id,item.date_time))
        for item in versions:
            v.append((item.id,item.date_time))
        return render(request,'versions.html', context={'versions' : v , 'versionParticles':vp ,'translation' : trans.text, 'quesId':trans.id})

class GetVersion(View):
    def post(self,request):
        print('in get version ')
        id = request.POST['id']
        version = Version.objects.get(id=id)
        print(version.text)
        return HttpResponse(version.text)

class GetVersionParticle(View):
    def post(self,request):
        print('in get version ')
        id = request.POST['id']
        version = Version.objects.get(id=id)
        print(version.text)
        return HttpResponse(version.text)

class SaveVersionParticle(View):
    def post(self,request):
        print('in save version particle')
        id = request.POST['id']
        content = request.POST['content']
        translation = Translation.objects.get(id=id)
        versionParticle = VersionParticle.objects.create(translation=translation, text=content, date_time = datetime.datetime.now())
        versionParticle.save()
        return HttpResponse("done")

class Notifications(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'notifications.html', context={'notifs': Notification.objects.all().order_by('-pub_date')})
