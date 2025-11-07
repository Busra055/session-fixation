import pyngrok
# app_v2.py
from flask import Flask, request, redirect, url_for, session, make_response
import secrets
import time
from pyngrok import ngrok, conf

# --- UYGULAMA YAPILANDIRMASI ---
app = Flask(__name__)
# Flask Session güvenliğini sağlamak için rastgele anahtar
app.secret_key = secrets.token_hex(28)

# Test Kullanıcıları
USERS_V2 = {"tester": "securepass", "guest": "easy123"}

# URL Tabanlı (Güvensiz) Oturumları Tutmak İçin Sözlük
app.config['URL_SESSIONS_V2'] = {}

# Session timeout ayarı (saniye cinsinden)
SESSION_EXPIRY = 600 # 10 dakika

# === FLASK GÜVENLİK AYARLARI ===
app.config['SESSION_COOKIE_HTTPONLY'] = True  # JS erişimini engeller
app.config['SESSION_COOKIE_SECURE'] = False   # Localhost için False, ngrok/üretim için True yapın
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict' # Daha sıkı bir kısıtlama

# --- YENİ KURUMSAL CSS TASARIMI (Siyah/Turuncu) ---
NEW_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    * { margin:0; padding:0; box-sizing:border-box; font-family:'Montserrat',sans-serif; }
    body {
        background-color: #2c3e50; /* Koyu Mavi Gri */
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        padding: 2rem;
    }
    .container {
        background: #34495e; /* Daha koyu gri */
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        width: 100%;
        max-width: 380px;
        text-align: center;
        border-top: 5px solid #e67e22; /* Turuncu Çizgi */
    }
    h1 { color: #ecf0f1; margin-bottom: 0.5rem; font-size: 1.8rem; }
    h2 { color: #e67e22; margin: 1rem 0; font-size: 1.3rem; }

    /* GİRİŞ ALANLARI - Yeni Stil */
    .auth-input {
        width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #7f8c8d; border-radius: 8px;
        font-size: 1rem; background: #2c3e50; color: white;
    }
    .auth-input::placeholder { color: #bdc3c7; }
    .auth-input:focus { outline: none; border-color: #e67e22; box-shadow: 0 0 0 2px rgba(230,126,34,0.5); }

    .btn-submit {
        background: #e67e22; color: white; border: none; padding: 10px 20px;
        border-radius: 8px; font-size: 1rem; cursor: pointer; margin-top: 1.5rem;
        transition: 0.3s; width: 100%; font-weight: 700;
    }
    .btn-submit:hover { background: #d35400; }

    .status-box { margin-top: 20px; padding: 15px; border-radius: 8px; font-size: 0.9rem; text-align: left; }
    .status-vuln { background: #c0392b; border-left: 4px solid #e74c3c; } /* Kırmızı */
    .status-safe { background: #27ae60; border-left: 4px solid #2ecc71; } /* Yeşil */

    a { color: #e67e22; text-decoration: none; font-weight: 700; }
    a:hover { text-decoration: underline; }

    .cookie-display {
        font-family: monospace; font-size: 0.8rem; background: rgba(0,0,0,0.2);
        padding: 5px; border-radius: 4px; word-break: break-all; margin-top: 5px;
    }
    .instruction { font-size: 0.85rem; color: #f1c40f; margin-top: 10px; font-weight: 600; }
</style>
"""

# --- GÜVENLİ GİRİŞ (Session ID her istekte yenilenir) ---
@app.route('/auth', methods=['GET', 'POST'])
def secure_auth():
    if request.method == 'POST':
        username = request.form['k_adi']
        password = request.form['sifre']
        if username in USERS_V2 and USERS_V2[username] == password:

            # GÜVENLİK ADIMI: Session Fixation'ı önle
            session.clear()
            session['user'] = username
            session['login_time'] = int(time.time())

            # F5'te Cookie'yi yenileyecek ilk token'ı ata
            session['renewal_token'] = secrets.token_urlsafe(16)
            session.modified = True

            return redirect(url_for('panel'))

        return f"{NEW_STYLE}<div class='container'><h2>Hata!</h2><p style='color:#e74c3c;'>Giriş Bilgileri Yanlış.</p><p><a href='/auth'>Geri</a></p></div>", 401

    return f'''
    {NEW_STYLE}
    <div class="container">
        <h2>Kurumsal Güvenli Giriş</h2>
        <form method="post">
            <input name="k_adi" class="auth-input" placeholder="Kullanıcı Adı (tester)" required>
            <input name="sifre" type="password" class="auth-input" placeholder="Parola (securepass)" required>
            <button type="submit" class="btn-submit">Güvenli Oturum Başlat</button>
        </form>
        <div class="status-box status-safe">
            <b>Yöntem:</b> Cookie tabanlı Flask Session.<br>
            <b>Koruma:</b> Girişte ve her sayfada Session ID içeriği yenilenir.
        </div>
    </div>
    '''

# --- ZAFİYETLİ GİRİŞ (URL Session ID) ---
@app.route('/legacy_auth', methods=['GET', 'POST'])
def legacy_auth():
    if request.method == 'POST':
        username = request.form['k_adi']
        password = request.form['sifre']
        if username in USERS_V2 and USERS_V2[username] == password:

            # ZAFİYET: URL'de taşınacak rastgele bir Session ID oluştur
            legacy_sid = secrets.token_urlsafe(24)
            app.config['URL_SESSIONS_V2'][legacy_sid] = {'user': username, 'time': int(time.time())}

            # Başarılı girişten sonra Session ID'yi URL'ye ekleyerek yönlendir
            return redirect(url_for('panel', legacy_sid=legacy_sid))

        return f"{NEW_STYLE}<div class='container'><h2>Hata!</h2><p style='color:#e74c3c;'>Giriş Bilgileri Yanlış.</p><p><a href='/legacy_auth'>Geri</a></p></div>", 401

    return f'''
    {NEW_STYLE}
    <div class="container">
        <h2>Eski Tip (Güvensiz) Giriş</h2>
        <form method="post">
            <input name="k_adi" class="auth-input" placeholder="Kullanıcı Adı (tester)" required>
            <input name="sifre" type="password" class="auth-input" placeholder="Parola (securepass)" required>
            <button type="submit" class="btn-submit">Güvensiz Oturum Başlat</button>
        </form>
        <div class="status-box status-vuln">
            <b>Zafiyet:</b> Oturum ID'si URL'de taşınır.<br>
            Risk: Session Fixation & ID Sızıntısı.
        </div>
    </div>
    '''

# --- YÖNETİM PANELİ ---
@app.route('/panel')
def panel():

    # 1. GÜVENSİZ (URL tabanlı) Kontrol
    legacy_sid = request.args.get('legacy_sid')
    if legacy_sid and legacy_sid in app.config['URL_SESSIONS_V2']:

        user_data = app.config['URL_SESSIONS_V2'][legacy_sid]
        user = user_data['user']

        # Timeout Kontrolü
        if int(time.time()) - user_data['time'] > SESSION_EXPIRY:
            app.config['URL_SESSIONS_V2'].pop(legacy_sid)
            return redirect(url_for('legacy_auth'))

        return f'''
        {NEW_STYLE}
        <div class="container">
            <h1>Hoş Geldiniz, {user}</h1>
            <h2>Eski Panel (Lütfen Güvenli Girişi Kullanın)</h2>
            <div class="status-box status-vuln">
                <b>Aktif Oturum ID:</b><br>
                <span class="cookie-display">{legacy_sid}</span>
                <p class="instruction">URL'yi inceleyin: ID'niz linkte görünüyor!</p>
            </div>
            <a href="{url_for('cikis', legacy_sid=legacy_sid)}" class="btn-submit" style="margin-top: 30px;">Oturumu Kapat</a>
        </div>
        '''

    # 2. GÜVENLİ (Cookie tabanlı) Kontrol
    if 'user' in session:
        user = session['user']

        # GÜVENLİK ADIMI: Her istekte Session Cookie içeriğini yenile
        old_token = session.get('renewal_token', '---')
        session['renewal_token'] = secrets.token_urlsafe(16)
        session.modified = True

        current_cookie = request.cookies.get('session', 'N/A')[:45]

        return f'''
        {NEW_STYLE}
        <div class="container">
            <h1>Hoş Geldiniz, {user}</h1>
            <h2>Güvenli Yönetim Paneli</h2>
            <div class="status-box status-safe">
                <b>Session Cookie İçeriği (İlk 45 Karakter):</b>
                <div class="cookie-display">{current_cookie}...</div>
                <p class="instruction">F5 yapın! Cookie içeriğinin sürekli değiştiğini DevTools -> Application -> Cookies sekmesinde görün.</p>
                <p style="margin-top: 10px;">**Eski Yenileme Jetonu:** {old_token[:8]}...</p>
            </div>
            <a href="{url_for('cikis')}" class="btn-submit" style="margin-top: 30px;">Güvenli Çıkış Yap</a>
        </div>
        '''

    # Varsayılan Giriş Sayfası
    return f'''
    {NEW_STYLE}
    <div class="container">
        <h1>Oturum Demo v2</h1>
        <p style="margin-bottom: 25px;">Lütfen giriş türünü seçin.</p>
        <a href="/auth" class="btn-submit" style="background: #e67e22;">🔐 Güvenli Giriş</a>
        <a href="/legacy_auth" class="btn-submit" style="background: #c0392b; margin-top: 10px;">🔓 Güvensiz Giriş</a>
    </div>
    '''

# --- ÇIKIŞ ---
@app.route('/cikis')
def cikis():
    legacy_sid = request.args.get('legacy_sid')

    if legacy_sid and legacy_sid in app.config['URL_SESSIONS_V2']:
        app.config['URL_SESSIONS_V2'].pop(legacy_sid, None)
        return redirect(url_for('legacy_auth'))

    else:
        session.clear()
        resp = make_response(redirect(url_for('secure_auth')))
        # Flask, session.clear() sonrası otomatik siler, ancak emin olmak için:
        resp.delete_cookie('session')
        return resp

# --- UYGULAMAYI BAŞLATMA ---
if __name__ == '__main__':
    # Ngrok kullanılıyorsa, SESSION_COOKIE_SECURE = True olmalı.
    app.config['SESSION_COOKIE_SECURE'] = True

    # ⚠️ NGrok Tokenınızı buraya yapıştırın ve yorum satırını kaldırın!
    # Kendi tokenınızı kullanın
    try:
        conf.get_default().auth_token = "356kAhx4iPOU0L0Md3ggDCfpc9S_6FXshei4eduLyis19qeJV"
        tunnel = ngrok.connect(5000, "http")

        print("\n" + "═"*70)
        print("🚀 YENİ GÜVENLİK DEMO BAŞLATILDI!")
        print(f"HTTPS URL: {tunnel.public_url}")
        print("═"*70)
        print(f"Güvenli Giriş: {tunnel.public_url}/auth")
        print(f"Güvensiz Giriş: {tunnel.public_url}/legacy_auth")
        print("═"*70 + "\n")

        app.run(host='0.0.0.0', port=5000, debug=False)

    except Exception as e:
        print(f"⚠️ Ngrok Bağlantı Hatası: {e}. Uygulama yerel olarak başlatılıyor.")
        print("Lütfen ngrok tokenınızı kontrol edin veya 'pyngrok'u yükleyin.")
        app.run(host='0.0.0.0', port=5000, debug=True)