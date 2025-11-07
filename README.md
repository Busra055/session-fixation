# Session Fixation Demo

Bu proje, **Session Fixation (Oturum Sabitleme)** güvenlik açığını göstermek ve nasıl düzeltileceğini uygulamalı olarak göstermek için hazırlanmış basit bir Flask uygulamasıdır.

---

## 🔐 Session Fixation Nedir?

**Session Fixation**, bir saldırganın kurbanın oturum kimliğini (session ID) önceden belirleyerek sistem içinde yetki kazanmasını sağlayan güvenlik açığıdır.

> Kısaca: Saldırgan kurbana sabit bir session ID kullandırır; kurban giriş yaptıktan sonra saldırgan aynı session ID ile yetkili olur.

Bu genelde şu yanlış uygulamalar nedeniyle gerçekleşir:

* Kullanıcı giriş yaptığında session ID yenilenmemesi
* Session ID’nin URL içine gömülmesi
* Session yönetiminin zayıf olması

---

## 📁 Proje Yapısı

```
├── app.py        → Hem zafiyetli hem de düzeltilmiş örnek içerir
└── README.md


## 🚨 Zafiyetli Bölüm

Projedeki ilk yaklaşımda:

* Kullanıcı giriş yaptığında **session ID yenilenmez**
* Saldırgan, kurbana kendi belirlediği session ID’yi içeren linki göndererek saldırıyı gerçekleştirebilir
* Kurban giriş yaptığında saldırgan aynı session ID ile yetki kazanabilir

> Bu, Session Fixation açığının temel örneğidir.

---

## ✅ Güvenli Bölüm

Kodun ilerleyen kısmında güvenli yöntem gösterilir.

Bu yaklaşımda:
✅ Kullanıcı giriş yaptığında **session ID yenilenir**
✅ Kullanıcı çıkış yaptığında session temizlenir
✅ Session ID, saldırgan tarafından tahmin edilemez / sabitlenemez

> Böylece saldırganın önceden belirlediği session ID geçersiz olur.

---

## 🔍 Kod Üzerinde İnceleme

Uygulama tek dosyadan oluşur: **app.py**

Dosya içinde önce zafiyetli örnek, ardından güvenli örnek verilmiştir.

### 1) Zafiyetli yaklaşım özet:

* Session ID sabit
* Kullanıcı giriş yaptığında değişmiyor
* Yetki devri mümkün

### 2) Güvenli yaklaşım özet:

* Session ID kullanıcı girişinde yenileniyor
* Eski session geçersiz hale getiriliyor
* Fixation engellenmiş oluyor

---

## ▶️ Çalıştırma

### Gerekli paketler:

```bash
pip install flask pyngrok
```

### Uygulama çalıştırma:

```bash
python app.py
```

---

## 🔎 Test Senaryosu

### ✅ Zafiyetli

1. Saldırgan token üretir
2. Kurbana link gönderir
3. Kurban giriş yapar
4. Saldırgan aynı token ile yetkili olur → **Saldırı başarılı**

### ✅ Güvenli

1. Saldırgan token üretir
2. Kurbana link gönderir
3. Kurban giriş yapar
4. Session ID yenilenir
5. Saldırgan eski token ile giriş yapamaz → **Saldırı başarısız**

---

## 🔒 Nasıl Önlenir?

✔ Giriş sonrası session ID yenilenmeli
✔ Session cookie tabanlı olsun
✔ Çıkışta session temizlenmeli

---

## 🧩 Özet Tablosu

| Özellik                   | Zafiyetli Yaklaşım | Güvenli Yaklaşım |
| ------------------------- | ------------------ | ---------------- |
| Session ID yenileniyor mu | ❌                 | ✅              |
| Fixation mümkün mü        | ✅                 | ❌              | 
| Güvenlik seviyesi         | Düşük              | Yüksek           |


✅ Bu proje, eğitim ve örnek amaçlıdır.
