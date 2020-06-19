from flask import Flask
from flask import request, request, render_template, jsonify
from provinsiKota import *
from tableDataText import *
import json
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from urllib.request import urlopen

valid_kota = id_kota_atau_kabupaten
url = 'https://api.rajaongkir.com/starter/cost'
headers = {"key":"1c5a64693add038257cc24dda894dc77"}

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/index", methods=["GET","POST"])
def index():
    list_pangan = ["beras","daging ayam","daging sapi","telur","bawang merah", "bawang putih", "cabai merah", "cabai rawit", "minyak goreng", "gula pasir"]
    list_jasa = []
    harga_jakarta = 0
    harga_daerah = 0
    kota_tujuan = ""
    pangan_pilihan = ""
    hargaPanganID = ""
    if request.method == 'POST':
        pangan_pilihan = request.form['pangan_pilihan']
        provinsi_pilihan = request.form['provinsi_pilihan']
        berat_pangan = request.form['berat_pangan']
        for i in valid_kota:
            if int(i["city_id"]) == int(provinsi_pilihan):
                kota_tujuan = i["province"]
                hargaPanganID= i["hargaPanganID"]
                
        #cek input masuk atau tidak
        print(pangan_pilihan + " " + provinsi_pilihan + berat_pangan)
        #request API
        payload = {
            "origin" : "152",
            "destination" : provinsi_pilihan,
            "weight" : berat_pangan,
            "courier" : "jne",
        }
        r = requests.post(url, payload, headers=headers)
        #cek request berhasil atau tidak
        response = r.json()
        jenis_jasa = response["rajaongkir"]["results"][0]['costs']
        for i in jenis_jasa:
            list_jasa.append({ "nama_jenis" : i["service"] , "harga" : i["cost"][0]["value"] })
        print(list_jasa)

        #scrap website hargapangan lalu update harga_jakarta dan harga_daerah
        path = "D:\Kampus\eai\EAI-Komparasi-harga-beli-daerah-dan-harga-beli-jakarta-plus-ongkir"
        driver = webdriver.Firefox(path)
        driver.get("https://hargapangan.id/tabel-harga/pasar-tradisional/daerah")        
        provinsiJakarta = Select(driver.find_element_by_id("filter_province_ids"))
        provinsiJakarta.select_by_value("13") # 13 = dki jakarta
        submit = driver.find_element_by_id("btnReport")
        submit.click()
        htmlDumpJakarta = driver.page_source
        print("HTML DUMP JAKARTA GET")
        provinsiTarget = Select(driver.find_element_by_id("filter_province_ids"))
        provinsiTarget.select_by_value(hargaPanganID) # 13 = dki jakarta
        submit = driver.find_element_by_id("btnReport")
        submit.click()
        htmlDumpTujuan = driver.page_source
        print("HTML DUMP TARGET GET")
        driver.quit()


        # html=urlopen("https://hargapangan.id/tabel-harga/pasar-tradisional/daerah")
        list_pangan_numbered = {"beras": 'I',"daging ayam":'II',"daging sapi":'III',"telur":'IV',"bawang merah":'V', "bawang putih":'VI', "cabai merah":'VII', "cabai rawit":'VIII', "minyak goreng":'IX', "gula pasir":'X'}

        bs=BeautifulSoup(htmlDumpJakarta, features="html.parser")
        daftar=bs.find("table",{"id": "report"})
        panganDataTable = tableDataText(daftar)
        nomorPangan =list_pangan_numbered.get(pangan_pilihan)
        target = []

        for cari in panganDataTable :
            if cari[0] == nomorPangan :
                target = cari
        hargaTarget = int(target[2].replace(".",""))
        harga_jakarta = hargaTarget

        bs=BeautifulSoup(htmlDumpTujuan, features="html.parser")
        daftar=bs.find("table",{"id": "report"})
        panganDataTable = tableDataText(daftar)
        nomorPangan =list_pangan_numbered.get(pangan_pilihan)
        target = []

        for cari in panganDataTable :
            if cari[0] == nomorPangan :
                target = cari
        hargaTarget = int(target[2].replace(".",""))
        harga_daerah = hargaTarget


        print(hargaTarget)

        # print(panganDataTable)


        
    
    list_param = [valid_kota,list_pangan,list_jasa,pangan_pilihan,harga_daerah,harga_jakarta,kota_tujuan]
    return render_template('index.html', list_param = list_param)


app.run()