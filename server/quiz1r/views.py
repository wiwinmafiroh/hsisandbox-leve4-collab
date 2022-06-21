from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import *

import json
import random

# Create your views here.
def users_json(request):
  usq = list(User.objects.values())
  
  return JsonResponse(usq, safe=False)

def peserta_json(request):
  psq = list(Peserta.objects.values())
  
  return JsonResponse(psq, safe=False)

def banksoal_json(request):
  try : #eva
    bsq = list(BankSoal.objects.values())
    bsr = random.sample(bsq, 2)
    status = True #eva 
    context = { #eva
      'bsr' : bsr,#eva
      'status' : status#eva
    }#eva
    
  except :#eva
    status = False#eva
    context = {#eva
      'status' : status#eva
    }#eva
  
  #return JsonResponse(bsr, safe=False) #awal
  return JsonResponse(context, safe=False)#eva
  
def login(request):
  try :
    status = 'error'
    
    if request.method == 'POST':
      data = json.loads(request.body)
      username = data['username'].lower()
      password = data['password']
      
      user = authenticate(request, username=username, password=password)
      
      if user is not None:
        if user.groups.filter(name='admin') :
          status=True
          context = {
            'peserta' : 'admin',
            'status' : status
          }
        else :
          psq = list(Peserta.objects.filter(user=user).values())
          status = True
          context = {
            'peserta': psq[0],
            'status' : status 
          }
      else:
          context = {
            'peserta': '',
            'status' : False 
          }
      return JsonResponse(context, safe=False)
    else:
      context = {
            'peserta': '',
            'status' : False 
          }
      return JsonResponse(context, safe=False)
  except :
    context = {
            'peserta': '',
            'status' : False 
          }
    return JsonResponse(context,safe=False)
    
    
#eva
def show_rank(request) :
  try : #eva
    rq = NilaiEvaluasi.objects.all().order_by('-total_nilai')
    status = True #eva
    list_rank=[]
    for rank in rq :
      nip= rank.peserta.nip 
      nama_lengkap= rank.peserta.nama_lengkap 
      total_nilai=rank.total_nilai
      dict={
        'nip' : nip,
        'nama_lengkap' : nama_lengkap,
        'total_nilai' :total_nilai
      }
      list_rank.append(dict)
    
    print(list_rank)
    context = { #eva
      'list_rank' : list_rank,#eva
      'status' : status#eva
    }#eva
  except :#eva
    print('masuk server error')
    status = False#eva
    context = {#eva
      'status' : status#eva
    }#eva

  #return JsonResponse(bsr, safe=False) #awal
  return JsonResponse(context, safe=False)#eva


def check_evaluasi(request):
  if request.method == 'GET':
    peserta_id = request.GET['peserta_id']
    psq = Peserta.objects.get(id=peserta_id)
    heq = HasilEvaluasi.objects.filter(peserta=psq)
    
    if heq.count() > 0:
      status = True
      context = {'status': status}
    else:
      status = False
      context = {'status': status}
    
    return JsonResponse(context, safe=False)
  
def check_jawaban(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    bank_soal = data['banksoal_id']
    jawaban_user = data['jawaban_user'].upper()
    
    bsq = BankSoal.objects.get(id=bank_soal)
    
    if jawaban_user == bsq.kunci_jawaban:
      status = "Benar"
      nilai = 2
      context = {
        'status': status, 
        'nilai': nilai,
      }
      
    else:
      status = "Salah"
      kunci_jawaban = bsq.kunci_jawaban
      nilai = 1
      context = {
        'status': status, 
        'kunci_jawaban': kunci_jawaban,
        'nilai': nilai,
      }
    
    return JsonResponse(context, safe=False)
  
def insert_evaluasi(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    peserta = data['peserta']
    lembar_evaluasi = "EH001"
    bank_soal = data['bank_soal']
    jawaban = data['jawaban'].upper()
    status = data['status']
    nilai = data['nilai']
    
    psq = Peserta.objects.get(id=peserta)
    bsq = BankSoal.objects.get(id=bank_soal)
    
    heq = HasilEvaluasi(peserta=psq, lembar_evaluasi=lembar_evaluasi, bank_soal=bsq, jawaban=jawaban, status=status, nilai=nilai)
    heq.save()
    
    context = {'status': True}
    return JsonResponse(context, safe=False)
  
def insert_nilaiexam(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    peserta = data['peserta']
    total_nilai = data['total_nilai']
    
    psq = Peserta.objects.get(id=peserta)
    neq = NilaiEvaluasi(peserta=psq, total_nilai=total_nilai)
    neq.save()
    
    context = {'status': True}
    return JsonResponse(context, safe=False)

def arsipniai_client(request):

    context={}
    # try:
    if request.method == 'POST':
      data = json.loads(request.body)
      peserta_id = data["peserta_id"]
      # print(peserta_id)
      hasileval = list(HasilEvaluasi.objects.filter(peserta=peserta_id).values())
      # print(hasileval)
      # pilihan_a = HasilEvaluasi.objects.filter(peserta=peserta_id).values("bank_soal__pilihan_a")
      # print(pilihan_a)
      # hasileval = list(HasilEvaluasi.objects.select_related('Peserta', 'BankSoal').filter(peserta=peserta_id).values())
      # print("hasil eval niiih"+hasileval.query)      

      id_soal = []
      pertanyaan = []
      kj = []
      textkj = []
      duasoal = []
      textj = []
      for i in range(2):
          id_soal.append(hasileval[i].get("bank_soal_id"))
          soal = BankSoal.objects.get(id=id_soal[i])
          # print(id_soal)
          jawaban = hasileval[i].get("jawaban")
          # Ambil text jawaban berdasarkan jawaban
          if jawaban == "A":
              textjawaban = soal.pilihan_a
          elif jawaban == "B":
              textjawaban = soal.pilihan_b
          elif jawaban == "C":
              textjawaban = soal.pilihan_c
          elif jawaban == "D":
              textjawaban = soal.pilihan_d
          textj.append(textjawaban)
          # print("pilihan aaaa = "+hasileval[i].va("bank_soal__pilihan_a"))
          # valuessoal = list(BankSoal.objects.filter(id=id_soal[i]).values())
          # duasoal.append(valuessoal)
          # print(duasoal)
          pertanyaan.append(soal.pertanyaan)
          kj.append(soal.kunci_jawaban)
          if kj[i] == "A":
            textkj.append(soal.pilihan_a)
          elif kj[i] == "B":
            textkj.append(soal.pilihan_b)
          elif kj[i] == "C":
            textkj.append(soal.pilihan_c)
            # print("ini jawaban C :"+soal.pilihan_c)
          elif kj[i] == "D":
            textkj.append(soal.pilihan_d)

      if not hasileval:
          context={
              'is_exam':0,
              'message':"\nAnda belum mengerjakan EH 1\n",
          }   
      else:
          context={
              'pertanyaan':pertanyaan,
              'kunci_jawaban':kj,
              'textkj':textkj,
              'textjawaban':textj,
              'is_exam':1,
              'hasileval':hasileval,
              'duasoal':duasoal,
              'message':("\nAnda telah mengerjakan EH 1\n"),
          }
          
    # except:
    #     context={
    #         'is_exam':0,
    #         'message':"\nAnda belum mengerjakan EH 1\n",
    #     }

    return JsonResponse(context, safe=False)