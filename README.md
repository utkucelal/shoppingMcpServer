# Shopping MCP Server

Amazon Türkiye ve Trendyol üzerindeki alışveriş işlemlerini Selenium aracılığıyla otomatikleştiren, aynı yetenekleri hem **MCP araçları** hem de **REST API** olarak sunan Python projesi.

> [!WARNING]
> Bu proje tarayıcı otomasyonu yapar ve satın alma akışı içerir. Gerçek hesaplarla kullanmadan önce kodu ve sepeti kontrol edin. Site arayüzlerindeki değişiklikler Selenium seçicilerini bozabilir.

## Özellikler

- Desteklenen alışveriş sitelerini listeleme
- Ürün arama
- Sepete ürün ekleme ve sepeti görüntüleme
- Siparişleri yerel veritabanından okuma veya siteden yenileme
- Sipariş detayı ve kargo takibi
- Sepet özeti oluşturma
- Kod ve PIN ile iki aşamalı satın alma onayı
- Aynı servis üzerinden REST ve Streamable HTTP MCP erişimi

## Teknolojiler

- Python
- Starlette ve Uvicorn
- Model Context Protocol (MCP)
- Selenium ve Google Chrome/Chromium
- SQLModel ve SQLite

## Gereksinimler

- Python 3.10 veya daha yeni bir sürüm
- Google Chrome ya da Chromium
- Chrome sürümüyle uyumlu Selenium Manager/ChromeDriver

Giriş gerektiren işlemlerde proje ayrı bir Chrome profili kullanır:

```text
~/Chromes/ShoppinMcp
```

İlk kullanımda açılan Chrome penceresinde ilgili alışveriş sitesine manuel olarak giriş yapmanız gerekebilir. Oturum bilgileri bu profilde saklanır.

## Kurulum

Projeyi klonlayın ve dizine geçin:

```bash
git clone <repo-url>
cd shoppingMcpServer
```

Sanal ortam oluşturup bağımlılıkları yükleyin:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell kullanıyorsanız sanal ortamı şu komutla etkinleştirin:

```powershell
.venv\Scripts\Activate.ps1
```

Veritabanı tabloları mevcut değilse oluşturun:

```bash
python data/models.py
```

## Çalıştırma

```bash
python server.py
```

Sunucu varsayılan olarak `http://localhost:8000` adresinde çalışır.

Geliştirme sırasında otomatik yeniden yükleme için:

```bash
uvicorn server:starlette_app --host 0.0.0.0 --port 8000 --reload
```

## MCP Bağlantısı

Streamable HTTP MCP uç noktası:

```text
http://localhost:8000/mcp
```

Sunucu aşağıdaki MCP araçlarını sağlar:

| Araç | Parametreler | Açıklama |
|---|---|---|
| `available_sites` | - | Desteklenen site anahtarlarını listeler |
| `search_products` | `query`, `max_results`, `site` | Ürün arar |
| `Add_Item` | `ProductID`, `quantity`, `site` | Sepete ürün ekler |
| `Check_Cart` | `site` | Sepeti getirir |
| `Fetch_Orders` | `site`, `refresh` | Siparişleri getirir; `refresh=true` siteyi yeniden tarar |
| `Order_Details` | `OrderID`, `site` | Sipariş detayını getirir |
| `Track_Order` | `OrderID`, `site` | Kargo durumunu getirir |
| `Checkout` | `site` | Satın alma özetini ve onay bilgilerini oluşturur |
| `confirm_purchase` | `code`, `pin`, `site` | Bekleyen satın alma işlemini onaylar |

Site değeri olarak yapılandırma dosyasındaki küçük harfli anahtarları kullanın: `amazon` veya `trendyol`.

> [!NOTE]
> Uzak bir istemciden bağlanacaksanız `server.py` içindeki `allowed_hosts` ayarını sunucunun gerçek host/IP ve port bilgisine göre düzenleyin. Mevcut değer geliştirme ortamına özeldir.

## REST API

Tüm REST uç noktaları `GET` isteği kabul eder.

| Uç nokta | Query parametreleri |
|---|---|
| `/api/sites` | - |
| `/api/search` | `query`, `max_results`, `site` |
| `/api/cart` | `site` |
| `/api/add-item` | `product_id`, `quantity`, `site` |
| `/api/fetch-orders` | `site`, `refresh` |
| `/api/order-details` | `order_id`, `site` |
| `/api/track-order` | `order_id`, `site` |
| `/api/checkout` | `site` |
| `/api/confirm-purchase` | `code`, `pin`, `site` |
| `/confirm/{hash}` | Tarayıcıda onay özeti ve PIN gösterir |

Örnek istekler:

```bash
curl "http://localhost:8000/api/sites"

curl "http://localhost:8000/api/search?query=kablosuz%20kulaklik&max_results=5&site=amazon"

curl "http://localhost:8000/api/add-item?product_id=PRODUCT_ID&quantity=1&site=amazon"

curl "http://localhost:8000/api/fetch-orders?site=amazon&refresh=true"
```

Satın alma akışı iki adımdır:

1. `/api/checkout` veya `Checkout` aracı sipariş özetini, onay kodunu ve `/confirm/{hash}` bağlantısını oluşturur.
2. Onay sayfasındaki PIN, kodla birlikte `/api/confirm-purchase` veya `confirm_purchase` aracına gönderilir.

## Proje Yapısı

```text
.
├── server.py                 # Starlette uygulaması ve MCP mount noktası
├── api.py                    # REST API ve onay sayfası
├── mcp_tools.py              # MCP araç tanımları
├── browser/
│   ├── manager.py            # Selenium WebDriver yönetimi
│   └── chrome.py             # Kalıcı Chrome profili ve debug oturumu
├── sites/
│   ├── amazon.py             # Amazon adaptörü
│   ├── trendyol.py           # Trendyol adaptörü
│   └── registry.py           # Site yapılandırması
└── data/
    ├── available-sites.json # Desteklenen siteler
    ├── models.py             # SQLModel modelleri
    └── main.db               # Yerel SQLite veritabanı
```

## Yeni Site Ekleme

1. `data/available-sites.json` dosyasına site anahtarını ve temel URL'yi ekleyin.
2. `sites/` altında sitenin Selenium işlemlerini uygulayan bir adaptör oluşturun.
3. `search.py`, `cart.py`, `addItem.py` ve ilgili diğer yönlendirme modüllerine yeni adaptörü ekleyin.
4. Arama, sepet, sipariş ve onay akışlarını gerçek site üzerinde ayrı ayrı doğrulayın.

## Bilinen Kısıtlar

- Otomasyon, sitelerin güncel HTML yapısına ve metinlerine bağımlıdır.
- Giriş, CAPTCHA ve iki faktörlü doğrulama bazı durumlarda manuel müdahale gerektirebilir.
- Aynı makinede `9222` portunu kullanan başka bir Chrome debug oturumu olmamalıdır.
- `data/main.db` yerel sipariş ve onay bilgileri içerebilir; bu dosyayı herkese açık depolarda paylaşmayın.
- Site desteği işlem bazında farklılık gösterebilir; özellikle satın alma ve onay akışı Amazon odaklıdır.

## Güvenlik

- Chrome profilini ve SQLite veritabanını hassas veri olarak değerlendirin.
- Sunucuyu internete doğrudan açmayın; gerekiyorsa kimlik doğrulama, TLS ve ağ erişim kuralları ekleyin.
- Satın alma onay kodlarını ve PIN'leri loglara veya kaynak kontrolüne yazmayın.
- Gerçek sipariş vermeden önce ürün, adet, adres, ödeme yöntemi ve toplam tutarı kontrol edin.
