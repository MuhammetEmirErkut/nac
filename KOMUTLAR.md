# 🎬 NAC Projesi - Sunum Komutları

**Tüm komutlar test edildi ve çalışıyor.**  
**Video süresi:** 10-15 dakika

---

## ⏱️ Çekim Öncesi Son Kontroller

```bash
# Servisleri başlat
docker-compose up -d

# Hepsinin "Up (healthy)" olduğunu doğrula
docker-compose ps

# Eski test verilerini temizle
docker exec nac_postgres psql -U radius -d radius -c \
"DELETE FROM radcheck WHERE username IN ('testuser', 'AA-BB-CC-DD-EE-FF');"

docker exec nac_postgres psql -U radius -d radius -c \
"DELETE FROM radusergroup WHERE username = 'testuser';"

docker exec nac_postgres psql -U radius -d radius -c \
"DELETE FROM radgroupreply WHERE groupname = 'Engineering';"

docker exec nac_redis redis-cli -a redis123! FLUSHALL 2>/dev/null
```

---

## 📍 1. MİMARİ AÇIKLAMASI (0:00 - 1:30)

*Bu bölümde komut yok - Mimari diyagram veya README.md gösterilir.*

---

## 📍 2. DOCKER COMPOSE YAPISI (1:30 - 3:00)

*Bu bölümde komut yok - docker-compose.yml dosyası gösterilir.*

---

## 📍 3. CANLI DEMO - AUTH & RATE LIMITING (3:00 - 6:00)

### Test Kullanıcı Ekle

```bash
docker exec nac_postgres psql -U radius -d radius -c \
"INSERT INTO radcheck (username, attribute, op, value) VALUES ('testuser', 'Cleartext-Password', ':=', 'testpass');"
```

### Başarılı Auth Testi

```bash
docker run --rm --network nac_nac_network \
freeradius/freeradius-server:latest-3.2 \
radtest testuser testpass nac_freeradius 0 testing123
```

### Policy Engine Loglarını Kontrol Et

```bash
docker-compose logs --tail=5 policy_engine | grep "/auth"
```

### Rate Limiting Testi (5 Yanlış Deneme)

```bash
for i in {1..5}; do \
  echo "Deneme $i:"; \
  docker run --rm --network nac_nac_network \
  freeradius/freeradius-server:latest-3.2 \
  radtest testuser yanlispass nac_freeradius 0 testing123 \
  2>&1 | grep -E "(Access-Accept|Access-Reject)"; \
done
```

### Redis Counter Kontrol

```bash
docker exec nac_redis redis-cli -a redis123! GET "rate_limit:testuser" 2>/dev/null
```

### 6. Deneme (Rate Limited)

```bash
echo "6. deneme:"; \
docker run --rm --network nac_nac_network \
freeradius/freeradius-server:latest-3.2 \
radtest testuser yanlispass nac_freeradius 0 testing123 \
2>&1 | grep -E "(Access-Accept|Access-Reject)"
```

---

## 📍 4. AUTHORIZATION VE VLAN ATAMASI (6:00 - 8:00)

### Kullanıcıyı Engineering Grubuna Ekle

```bash
docker exec nac_postgres psql -U radius -d radius -c \
"INSERT INTO radusergroup (username, groupname, priority) VALUES ('testuser', 'Engineering', 1);"
```

### Engineering Grubuna VLAN 100 Ata

```bash
docker exec nac_postgres psql -U radius -d radius -c \
"INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES ('Engineering', 'Tunnel-Private-Group-Id', '=', '100');"
```

### Authorize Endpoint'ini Test Et

```bash
curl -s http://localhost:8000/authorize -X POST \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "password": "testpass"}'
```

---

## 📍 5. ACCOUNTING (VERİ TOPLAMA) (8:00 - 10:30)

### MAC Adresi İçin MAB Kullanıcısı Ekle

```bash
docker exec nac_postgres psql -U radius -d radius -c \
"INSERT INTO radcheck (username, attribute, op, value) VALUES ('AA-BB-CC-DD-EE-FF', 'Cleartext-Password', ':=', 'AA-BB-CC-DD-EE-FF');"
```

### Accounting-Start Gönder

```bash
echo "Acct-Status-Type = Start
Acct-Session-Id = MAB-SESSION-001
User-Name = AA-BB-CC-DD-EE-FF
Calling-Station-Id = AA-BB-CC-DD-EE-FF
NAS-IP-Address = 192.168.1.1
Acct-Input-Octets = 0
Acct-Output-Octets = 0
Acct-Session-Time = 0" | \
docker run --rm -i --network nac_nac_network \
freeradius/freeradius-server:latest-3.2 \
radclient nac_freeradius:1813 acct testing123
```

### Aktif Oturumları Kontrol Et (Redis)

```bash
curl -s http://localhost:8000/sessions/active
```

### PostgreSQL radacct Kontrolü

```bash
docker exec nac_postgres psql -U radius -d radius -c \
"SELECT username, acctstarttime, acctsessionid, nasipaddress FROM radacct ORDER BY radacctid DESC LIMIT 1;"
```

### Accounting-Stop Gönder

```bash
echo "Acct-Status-Type = Stop
Acct-Session-Id = MAB-SESSION-001
User-Name = AA-BB-CC-DD-EE-FF
Calling-Station-Id = AA-BB-CC-DD-EE-FF
NAS-IP-Address = 192.168.1.1
Acct-Input-Octets = 1048576
Acct-Output-Octets = 5242880
Acct-Session-Time = 300
Acct-Terminate-Cause = User-Request" | \
docker run --rm -i --network nac_nac_network \
freeradius/freeradius-server:latest-3.2 \
radclient nac_freeradius:1813 acct testing123
```

### Session Sonrası Aktif Oturumlar (2 saniye bekle)

```bash
sleep 2
curl -s http://localhost:8000/sessions/active
```

### PostgreSQL'de Tüm Accounting Kayıtları

```bash
docker exec nac_postgres psql -U radius -d radius -c \
"SELECT username, acctstarttime, acctstoptime, acctsessiontime FROM radacct;"
```

### Dashboard'u Aç (Tarayıcıda)

```bash
# Mac
open http://localhost:8000/dashboard

# Linux
# xdg-open http://localhost:8000/dashboard

# Windows
# start http://localhost:8000/dashboard
```

---

## 📍 6. ZORLUKLAR & ÇÖZÜMLER (10:30 - 12:30)

### Logları İncele (Örnek)

```bash
docker-compose logs freeradius | grep "rlm_rest"
```

### Container İçi Ping Testi

```bash
docker exec nac_policy_engine ping -c 3 postgres
```

---

## 📍 7. MİMARİ KARARLAR (12:30 - 14:00)

*Bu bölümde komut yok - Sözlü anlatım.*

---

## 📍 KAPANIŞ (14:00 - 15:00)

### Final Durum Kontrolü

```bash
docker-compose ps
```

### Health Check

```bash
curl -s http://localhost:8000/health | jq
```

---

## 🛠️ Yedek Komutlar (Acil Durumlar)

### Servisler Çökerse

```bash
docker-compose restart
```

### Tam Sıfırlama

```bash
docker-compose down -v && docker-compose up -d --build
```

### Redis Rate Limit Sıfırla

```bash
docker exec nac_redis redis-cli -a redis123! FLUSHALL 2>/dev/null
```

### Logları Temizle

```bash
docker-compose logs --tail=0 -f
```

### Policy Engine Logları (Canlı)

```bash
docker-compose logs -f policy_engine
```

### FreeRADIUS Logları (Canlı)

```bash
docker-compose logs -f freeradius
```

---

## 📌 Önemli Notlar

| Konu | Değer |
|------|-------|
| Docker network adı | `nac_nac_network` |
| Platform uyarısı (ARM Mac) | `platform does not match` - Normal, komut çalışıyor |
| Port 8000 | API ve Dashboard için açık |
| Accounting-Stop sonrası | Session 1-2 saniye içinde Redis'ten silinir |
| Redis password uyarısı | `2>/dev/null` ile gizlendi |

---

## 🎯 Sunum İpuçları

- Terminal fontu: **16pt** (izleyiciler okuyabilsin)
- Tema: **Dark mode** (göz yormaz)
- Komutları çalıştırmadan önce **ne yapacağınızı söyleyin**
- Takılırsanız **durun, nefes alın, devam edin**
- **En az 2 kere prova yapın**

---

**Başarılar! 🚀**
