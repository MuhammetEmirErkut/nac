# Network Access Control (NAC) Sistemi

Bu proje FreeRADIUS, FastAPI (Policy Engine), PostgreSQL ve Redis kullanarak modern bir AAA (Authentication, Authorization, Accounting) mimarisi kurmayı amaçlamaktadır. 

## Gereksinimler
- Docker
- Docker Compose

## Kurulum ve Çalıştırma

Aşağıdaki komut ile tüm servisleri (PostgreSQL, Redis, Policy Engine, ve yapılandırılmış FreeRADIUS) arka planda ayağa kaldırabilirsiniz:

```bash
docker-compose up -d --build
```

Servislerin sağlıklı bir şekilde çalışıp çalışmadığını kontrol etmek için:
```bash
docker-compose ps
```
PostgreSQL, Redis ve FastAPI ayağa kalktıktan sonra, `freeradius` servisi istek almaya başlayacaktır.

## Test Etme

Sistem FreeRADIUS üzerinden Policy Engine (FastAPI) aracılığıyla doğrulama yapar. 

Öncelikle SQL içerisindeki `radcheck` tablosuna bir test kullanıcısı ekleyelim:
```bash
docker exec -it nac_postgres psql -U radius -d radius -c "INSERT INTO radcheck (username, attribute, op, value) VALUES ('testuser', 'Cleartext-Password', ':=', 'testpass');"
```

Aşağıdaki komut ile yapılandırmayı yerel makineniz üzerinden test edebilirsiniz:

### PAP Kimlik Doğrulaması (Auth) Testi
```bash
docker run --rm --network nac_network freeradius/freeradius-server:latest-3.2 radtest testuser testpass nac_freeradius 0 testing123
```

### MAB (MAC Adresi) Doğrulaması Testi
MAB için parola ve kullanıcı adı Cihazın MAC Adresi olacaktır:
```bash
# Önce MAC adresini sisteme kaydedelim
docker exec -it nac_postgres psql -U radius -d radius -c "INSERT INTO radcheck (username, attribute, op, value) VALUES ('AA-BB-CC-DD-EE-FF', 'Cleartext-Password', ':=', 'AA-BB-CC-DD-EE-FF');"

# Doğrulama Testi
docker run --rm --network nac_network freeradius/freeradius-server:latest-3.2 radtest AA-BB-CC-DD-EE-FF AA-BB-CC-DD-EE-FF nac_freeradius 0 testing123
```

MAB işlemini `Calling-Station-Id` göndererek `radclient` ile daha spesifik test edebilirsiniz:
```bash
echo "User-Name=AA-BB-CC-DD-EE-FF, Calling-Station-Id=AA-BB-CC-DD-EE-FF" | docker run --rm -i --network nac_network freeradius/freeradius-server:latest-3.2 radclient nac_freeradius:1812 auth testing123
```

## Geliştirme Uç Noktaları (Endpoints)
- REST API (Policy Engine): `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`
