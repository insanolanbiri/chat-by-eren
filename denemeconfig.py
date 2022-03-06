# deneme ve inceleme için değişkenler dosyası.
# insanolanbiri/deneme/denemeconfig.py dosyasının düzenlenmiş sürümü.
url = "https://aydinyayinlari.karnemiz.com/?pg=ogrgiris"  # giriş yapılacak url
# not: scriptin çalışması için deneme sonuç urlsi `orbim` adındaki
#      bir şirketin yaptığı arayüzü kullanmalı.
headless = False  # selenium'un arka planda çalışıp çalışmayacağı
drv_path = (
    ""  # "geckodriver.exe" # selenium'un kullanacağı driver dosyası, ""=varsayılan
)
puanbosluk = 6  # aq sitesinde puan yazısı "Puanınız_vs: intPuan" olarak yazıldığı için bunu ekliyoruz.
i_sinif = "9.Sınıf"  # sınıf seviyesi, boşluk olmadan: "9.Sınıf" gibi.
i_sehir = "EDİRNE"  # şehir, tamamı büyük harf: "EDİRNE" gibi.
i_kurum = "Edirne Süleyman Demirel"  # okulun adı, siteye yazıldığında listede ilk sonuç olarak görünmeli.


# not: sınıf listelerini başka bir yerden bulup güncellemeniz lazım.
#      kendimi test amaçlı kullanabilirsiniz :)
sinif9a = [["Eren Akgün", 7]]
sinif9b = [["Eren Akgün", 7]]
sinif9c = [["Eren Akgün", 7]]
