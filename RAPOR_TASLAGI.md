# NAC Staj Değerlendirme Ödevi - Rapor Taslağı

> [!WARNING]
> **YAPAY ZEKA FİLTRESİ:** Raporunuz otomatik olarak yapay zeka tespit sisteminden geçirilecek ve %25 sınırı uygulanacaktır. Bu nedenden ötürü lütfen buradaki metinleri DOĞRUDAN KOPYALAMAYIN. Aşağıdaki başlıklardaki maddeleri okuyun, anlayın ve kendi anladığınız, doğal kelimelerinizle birleştirerek profesyonel bir rapor dökümanı haline getirin.

## 1. Giriş
- **Özetleyin:** Bu projenin amacı neydi? (Yetkisiz cihazların yerel ağa girmesini engellemek, 802.1X/MAB yardımıyla güvenliği artırmak).
- **Hangi teknolojileri kullandınız?** Docker, FreeRADIUS (yönlendirici olarak), FastAPI (mantığı işleyen beyin olarak), PostgreSQL ve Redis.
- **Odaklandığınız konular:** Kimlik doğrulama, dinamik VLAN ataması gibi AAA konseptlerini yerine getirmek.

## 2. Mimari Tasarım
- **Veri Akışından Bahsedin:** Cihaz -> NAS (Switch/AP) -> FreeRADIUS (UDP 1812) -> FastAPI (rlm_rest modülü POST) -> Postgres (Veritabanı Doğrulaması).
- **Docker Compose Kararı:** Sistem bağımlılıkları `depends_on` ve `healthcheck` mekanizmaları ile korundu. Yani veritabanları tam anlamıyla hazır olmadan FastAPI hizmet vermiyor, API hazır olmadan da FreeRADIUS başlatılmıyor. İç ağda DNS üzerinden (örn. `nac_network`) güvenle konuşuyorlar.

## 3. Uygulama Detayları
- **Authentication (PAP ve MAB):** FastAPI tarafında `/auth` ucu yazdınız. Eğer gelen pakette şifre varsa bunu SQL'de `Bcrypt` (veya testler için Cleartext) ile karşılaştırarak onay veriyor; şifre yoksa ve "Calling-Station-Id" gönderilmişse (MAB) sadece MAC adresini sistemdeki MAC listesiyle kıyaslıyor.
- **Authorization:** Başarılı girişten sonra `/authorize` ucuna düşen veriden kullanıcının grubu çekiliyor. Özel VLAN etiketleri (Örn: `Tunnel-Type=VLAN 10`) JSON olarak dönülüp FreeRADIUS'a yediriliyor.
- **Accounting & Redis:** Oturum (`Start`, `Interim-Update`, `Stop`) işlemleri SQL `radacct` tablosuna yazılıyor. Hızlı erişim için aktif oturumlar Redis'te tutuluyor. (Ayrıca sistem bir `Monitoring Dashboard` barındırıyor, bunu projenizde bonus özellikte eklediniz!).
- **Rate-Limiting:** Redis Cache kullanılarak 5 hatalı girişte MAC/kullanıcı bloke ediliyor. Kaba kuvvet (Brute Force) saldırılarına karşı bir koruma geliştirdiniz.

## 4. Güvenlik Değerlendirmesi
- **Şifreleme:** PostgreSQL içindeki parolalar düz metin (plaintext) değil, bcrypt Hash yapısıyla tutulabilmektedir.
- **İzolasyon:** Servisler arası HTTP isteklerinde hassas sistem sırları (VPN secretları vb.), `.env` ortam değişkenleriyle saklandı, Git repoya yüklenmedi.
- **Risk & İyileştirme:** RADIUS paketleri ağ üzerinde düz (şifresiz) geçebilir, bir gerçek ortamda (Production) NAS ve FreeRADIUS arasına IPSec / RadSec kurmak daha uygun olabilir.

## 5. Gerçek Dünya Uygulamaları
**(Aşağıdakilerden iki tanesini seçip kendi cümlelerinizle derinleştirin:)**
1. **Kurumsal Ağ Güvenliği:** Şirkete gelen misafirlerin doğrudan `Guest VLAN`'a alınması, IT çalışanlarının `Admin VLAN`'a alınması işlemleri MAB (cihazın tanınması) ve PAP (çalışanın girişi) ile yönetilir.
2. **Sağlık Sektörü (Hastane Ortamı):** Tomografi veya EKG cihazları kimlik doğrulaması yeteneğine sahip değildir. MAB yetkilendirmesi sayesinde sadece sistemde MAC adresi onaylı cihazlar ağa dahil olabilir. Bu, yetkisiz bilgisayarların tıbbi cihaza erişimini engelleyerek KVKK'yı korur.

## 6. Sonuç ve Öğrenilenler
- **Kendinizi değerlendirin:** RADIUS protokolünün yaşına rağmen `rlm_rest` entegrasyonu ve FastAPI gibi modern bir RESTful mimariyle nasıl modernleştirilebildiğini, ne kadar kolay ölçeklenebildiğini (scalable yapı) ve `Monitoring Dashboard` ile anlık yönetilebildiğini bu staj ödevinde tecrübe ettiğinizi kendi kelimelerinizle yazın.
