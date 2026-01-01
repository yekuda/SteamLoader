# SteamLoader

**SteamLoader**, Steam oyunlarını kolayca yüklemenizi ve yönetmenizi sağlayan modern bir masaüstü uygulamasıdır.

## 📋 Özellikler

- ✨ Sürükle-bırak ile kolay oyun yükleme
- 🎮 Otomatik DLC desteği (Steam API ile)
- 📋 Eklenen oyunları görüntüleme (Steam API ile oyun isimleri)
- 🗑️ Oyun silme ve temizleme araçları
- 🔄 Steam'i hızlıca yeniden başlatma
- 🎨 Modern ve kullanıcı dostu arayüz
- 🔒 Otomatik yapılandırma dosyası yönetimi
- 💾 Steam klasörü yolunun otomatik kaydedilmesi
- 🚀 Uygulama açıldığında kaydedilmiş ayarların otomatik yüklenmesi
- ⚡ Threading ile performans optimizasyonu

## ⚠️ Önemli Uyarılar

- ⚠️ **Bu yazılım online oyunlarda çalışmaz.**
- ⚠️ **Denuvo gibi gelişmiş koruma sistemine sahip oyunlarla uyumlu değildir.**

## 🚀 Kurulum

### Gereksinimler

- ⚠️ **OYUN DOSYASI**: Aşağıdaki sitelerden birinden oyunun ZIP dosyasını indirmeniz **ZORUNLUDUR** (olmazsa uygulama çalışmaz):
  - [Steam Manifest Hub](https://steamtools.pages.dev/)
  - [SteamML](https://steamml.vercel.app/)
- Windows işletim sistemi
- Python 3.8+ (kaynak koddan çalıştırıyorsanız)
- İnternet bağlantısı (DLC bilgileri ve oyun dosyası indirme için)

## 📖 Kullanım

### 1. Oyun Dosyası Hazırlama

- Aşağıdaki sitelerden **birinden** oyunun ZIP dosyasını indirin:
  - [Steam Manifest Hub](https://steamtools.pages.dev/)
  - [SteamML](https://steamml.vercel.app/)
- ZIP dosyasının adı **mutlaka AppID olmalıdır** (örnek: `730.zip`, `271590.zip`)
  - AppID'yi Steam Store sayfasındaki URL'den bulabilirsiniz
  - Örnek: `store.steampowered.com/app/730/` → AppID: **730**

### 2. Uygulama Adımları

#### Adım 1: Steam Klasörünü Seçin
- "Gözat" butonuna tıklayın
- Steam'in kurulu olduğu ana klasörü seçin (örnek: `C:\Program Files (x86)\Steam`)
- **Not**: Seçtiğiniz klasör otomatik olarak kaydedilir ve bir sonraki açılışta otomatik yüklenir
- Steam klasörü alanı sadece "Gözat" butonu ile düzenlenebilir (manuel yazı girişi yapılamaz)

#### Adım 2: Oyun Yükleme
- İndirdiğiniz ZIP dosyasını sürükleyip ortadaki alana bırakın
- VEYA alana tıklayıp manuel olarak seçin
- Uygulama otomatik olarak:
  - `.lua` dosyalarını `config/stplug-in/` dizinine
  - `.manifest` dosyalarını `config/depotcache/` dizinine kopyalar
  - DLC bilgilerini Steam API'den çeker ve `yekuda.lua` dosyasına ekler
  - `hid.dll` dosyasını Steam ana dizinine indirir (yoksa)

#### Adım 3: Steam'i Yeniden Başlatın
- "Steam'i Yeniden Başlat" butonuna tıklayın
- Oyununuz Steam kütüphanenizde görünecektir

### 3. Oyun Yönetimi

#### Eklenen Oyunları Görüntüleme
- "Eklenen Oyunları Göster" butonuna tıklayın
- Açılan dialog penceresinde eklenen tüm oyunlar görüntülenir
- Oyunlar Steam API'den çekilen isimleriyle birlikte gösterilir
- Oyunlar arka planda yüklenir, uygulama donmaz

#### Oyun Silme
- "Silinecek Oyun ID'sini Girin" alanına AppID'yi yazın
- "Oyunu Sil" butonuna tıklayın
- Ana oyun + tüm DLC'ler temizlenecektir

#### Toplu Temizleme
- "Tüm Eklenen Oyunları Temizle" butonu ile tüm yapılandırma dosyalarını silebilirsiniz

## 📁 Dosya Yapısı

```
SteamLoader/
├── main.py                  # Uygulama giriş noktası
├── main_window.py           # Ana pencere ve arayüz yönetimi
├── core/                    # Uygulamanın iş mantığı
│   ├── event_handlers.py
│   └── steam_operations.py
├── ui/                      # Arayüz bileşenleri
│   ├── dialogs.py
│   ├── style.py
│   ├── ui_components.py
│   └── widgets.py
├── utils/                   # Yardımcı fonksiyonlar
│   └── utils.py
├── README.md
└── favicon.ico
```

## ⚙️ Teknik Detaylar

### Desteklenen Dosya Formatları
- **Giriş**: `.zip` arşivleri (AppID olarak adlandırılmış)
- **Çıkarılan dosyalar**: `.lua` (yapılandırma), `.manifest` (depot)

### API Kullanımı
- Steam Store API: `https://store.steampowered.com/api/appdetails`
- DLC bilgileri otomatik olarak çekilir ve yapılandırmaya eklenir

### Otomatik İndirmeler
- `hid.dll` dosyası ilk yüklemede otomatik olarak indirilir
- Kaynak: `http://yekuda.com/dll/hid.dll`
- **Not**: Bu DLL dosyası tamamen virüssüzdür ve sadece programın düzgün çalışması için gereklidir

### Ayarlar ve Yapılandırma
- Steam klasörü yolu otomatik olarak kaydedilir
- Config dosyası konumu: `%LOCALAPPDATA%\SteamLoader\config.json` (Windows)
- Config dosyası formatı: JSON
- Uygulama her açılışta kaydedilmiş ayarları otomatik yükler

## 🛠️ Geliştirme

### Kaynak Koddan Çalıştırma

```bash
pip install -r requirements.txt
python main.py
```

### EXE Oluşturma

```bash
# Gereksinimler: PyInstaller
build_exe.bat
```

Çıktı: `dist/SteamLoader.exe`

## ⚠️ Önemli Notlar

1. **ZIP dosyası adlandırması**: Dosya adı mutlaka sadece sayılardan oluşmalı (AppID)
2. **Yedekleme**: İşlem öncesi `config` klasörünü yedeklemeniz önerilir
3. **İnternet bağlantısı**: DLC bilgileri için gereklidir
4. **Ayarların saklanması**: Steam klasörü yolu otomatik olarak `%LOCALAPPDATA%\SteamLoader\config.json` dosyasına kaydedilir
5. **İlk kullanım**: İlk açılışta Steam klasörünü seçmeniz gerekir, sonraki açılışlarda otomatik yüklenir

## 🎨 Arayüz

- **Koyu tema** ile göz yorgunluğunu azaltır
- **Sürükle-bırak** desteği ile hızlı işlem
- **Anında geri bildirim** ile kullanıcı dostu deneyim
- **Onay diyalogları** ile güvenli silme işlemleri
- **Read-only alanlar** ile yanlış girişleri önler
- **Otomatik ayar yükleme** ile kullanıcı deneyimini iyileştirir
- **Dialog pencereleri** ile temiz ve organize görünüm
- **Threading** ile akıcı performans (UI donmaz)

## ⚖️ Sorumluluk Reddi

Bu yazılım "olduğu gibi" sunulmaktadır. Kullanıcılar bu uygulamayı kullanarak tüm sorumluluğu kabul ederler. Herhangi bir yasal veya teknik sorundan kullanıcılar sorumludur.

## 🔗 Kaynaklar

- Oyun dosyaları:
  - [Steam Manifest Hub](https://steamtools.pages.dev/)
  - [SteamML](https://steamml.vercel.app/)
- Steam API Dokümantasyonu: [Steamworks API](https://partner.steamgames.com/doc/webapi)

## 💡 İpuçları

- **AppID Bulma**: Steam Store → Oyun sayfası → URL'deki sayı
- **Çoklu Oyun**: Her oyun için ayrı ZIP dosyası kullanın
- **DLC Sorunları**: İnternet bağlantınızı kontrol edin
- **Hata Durumu**: Steam klasör yolunu doğrulayın
- **Ayarları Sıfırlama**: `%LOCALAPPDATA%\SteamLoader\config.json` dosyasını silerek ayarları sıfırlayabilirsiniz
- **Klasör Değiştirme**: Steam klasörünü değiştirmek için "Gözat" butonunu kullanın
- **Eklenen Oyunları Kontrol**: "Eklenen Oyunları Göster" butonu ile yüklediğiniz oyunları kontrol edebilirsiniz
- **Oyun İsimleri**: Oyun isimleri Steam API'den otomatik olarak çekilir, internet bağlantısı gereklidir

---