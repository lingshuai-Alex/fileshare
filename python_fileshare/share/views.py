#conding=utf-8
from django.shortcuts import render
from django.views.generic import View
from .models import Upload
from django.http import HttpResponseRedirect, HttpResponse
import random
import string
import json
import datetime


class HomeView(View):
    def get(self,request):
        return render(request,"base.html",{})

    def post(self,request):
        if request.FILES:
            file = request.FILES.get("file")
            name = file.name
            size = int(file.size)
            check_size = file.multiple_chunks()
            if check_size:
                with open('static/file/' + name, 'wb')as f:
                    for line in file.chunks():
                        f.write(line)
            else:
                with open('static/file/'+name,'wb')as f :
                    for line in file.read():
                        f.write(line)
            f.close()
            code = ''.join(random.sample(string.digits, 8))
            u = Upload(
                path = 'static/file/'+name,
                name=name,
                Filesize=size,
                code = code,
                PCIP=str(request.META['REMOTE_ADDR']),
            )
            u.save()
            # return HttpResponsePermanentRedirect("/s/"+code)
            return HttpResponseRedirect("/s/" + code)

class DisplayView(View):
    def get(self,request,code):
        u = Upload.objects.filter(code=str(code))
        if u :
            for i in u :
                i.DownloadDocount +=1
                i.save()
        return render(request,'content.html',{"content":u})


class MyView(View):
    def get(self,request):
        IP = request.META['REMOTE_ADDR']#查询客户端ip地址
        u = Upload.objects.filter(PCIP=str(IP))
        for i in u :
            i.DownloadDocount +=1
            i.save()
        return render(request,'content.html',{"content":u})


class SearchView(View):
    def get(self,request):
        code = request.GET.get("kw")
        u = Upload.objects.filter(name=str(code))
        data = {}
        #构造json对象传输数据给页面
        if u :
            for i in range(len(u)):
                u[i].DownloadDocount +=1
                u[i].save()
                data[i]={}
                data[i]['download'] = u[i].DownloadDocount
                data[i]['filename'] = u[i].name
                data[i]['id'] = u[i].id
                data[i]['ip'] = str(u[i].PCIP)
                data[i]['size'] = u[i].Filesize
                data[i]['time'] = str(u[i].Datatime.strftime('%Y-%m-%d %H:%M:%S'))
                data[i]['key'] = u[i].code
        return HttpResponse(json.dumps(data),content_type="application/json")
# Create your views here.
