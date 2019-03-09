# インストール

必要なライブラリ等です．Anaconda環境の方は，適宜`pip`を`conda`に置き換えてください．

```
pip install django Pillow django-imagekit
```

# 実装

## 新規プロジェクトを作成する．

コマンドラインから，コードを置きたい場所にcdして，次のコマンドを実行します．
実行すると`mysite`ディレクトリが作成されます．

```
$ django-admin startproject mysite
```

## 開発用サーバー起動確認

`mysite`ディレクトリ内に入り，以下のコマンドを実行します．

```
$ python manage.py runserver
```

実行出来たら，ブラウザで`http://127.0.0.1:8000/`にアクセスしてみましょう．
(ロケットが表示されたら成功です！)

コマンドラインで`CONTROL-C`することで停止できます．

## 新規アプリを作成する.

アプリケーションを作る為に，`manage.py`のある場所で，次のコマンドを実行.

```
$ python manage.py startapp photos
```

## 画像投稿機能の実装

#### 画像(メディア)の保存場所作成

画像(メディア)を格納しておくディレクトリを作成する．このディレクトリをメディアルートといいます.

`mysite`直下に，`media`という名前でディレクトリを作成する．



`mysite/settings.py`に設定を追加します．

`INSTALLED_APPS`に`'photos.apps.PhotosConfig',`を追加します．

先ほど作成した`media`ディレクトリを使用する為の設定も追加します．
```
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

この様な感じです．

#### settings.py
```
INSTALLED_APPS = [
    'photos.apps.PhotosConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

/* 中略 */

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

`mysite/urls.py`にも設定を追加します．

#### urls.py

```
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

`photos/models.py`でモデルの定義を行います．

#### models.py

```
class Photo(models.Model):
    photo = models.ImageField(upload_to='uploads/%Y/%m/%d/')
```

モデルを作成したら，モデルをデータベースに適応します．

```
$ python manage.py makemigrations photos
$ python manage.py migrate
```

`photos`直下に`forms.py`を作成し，フォームの定義を行います．

#### forms.py

```
from django.forms import ModelForm
from .models import Photo

class PhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['photo',]

```

`photos/views.py`でviewの定義を行います．

#### views.py

```
from django.views.generic import ListView, CreateView
from .models import Photo
from .forms import PhotoForm

class PhotoListView(ListView):
    model = Photo
    context_object_name = 'photo_list'
    template_name = "photos/index.html"

class PhotoCreateView(CreateView):
    model = Photo
    form_class = PhotoForm
    template_name = "photos/form.html"
    success_url = '/'

```

`phots/templates/photos/index.html` を作成します．

#### index.html

```
{% for p in photo_list %}
    <div>
        <img src="{{ p.photo.url }}">
    </div>
{% endfor %}
```

`phots/templates/photos/form.html` を作成します．

#### form.html

```
<form method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    <table>
        {{ form.as_table }}
    </table>
    <input type="submit" value="投稿" />
</form>

```

photoアプリへのpath設定します．

#### mysite/urls.py

```
from django.urls import include

urlpatterns = [
    path('', include('photos.urls')),
    path('admin/', admin.site.urls),
]

```

`photos`直下に`urls.py`を作成します．．

#### photos/urls.py

```
from django.urls import path
from .views import PhotoListView, PhotoCreateView

urlpatterns = [
    path('', PhotoListView.as_view(), name='index'),
    path('create', PhotoCreateView.as_view(), name='form'),
]

```

#### 動作確認

`http://127.0.0.1:8000/`にアクセスすると投稿された画像が一覧表示されます．

`http://127.0.0.1:8000/create`にアクセスすることで，画像の投稿が行えます．


## 改良1

一応画像の投稿は出来ましたが，投稿された画像がサイズもそのままの状態で表示されてしまいます．小さな画像なら良いかもしれませんが，大きな画像だと画面一杯に表示され大変です．

投稿された画像をサイズ変更し，各画像サイズも統一して表示される様にしてみましょう．

設定を追加します．
`settings.py`の`INSTALLED_APPS`に`'imagekit'`を追加します．

#### settings.py
```
INSTALLED_APPS = [
    'photos.apps.PhotosConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'imagekit',
]
```

モデルを編集します．
`ImageSpecField()`で受け取った画像を`260px*260px`のサイズに切り抜いて保存しています．

#### models.py

```
from django.db import models
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill

class Photo(models.Model):
    photo = models.ImageField(upload_to='uploads/%Y/%m/%d/')

    photo_thumbnail = ImageSpecField(source='photo',
                            processors=[ResizeToFill(260,260)],
                            format='JPEG',
                            options={'quality': 85}
                            )
```

`p.photo.url` を `p.photo_thumbnail.url` に変更します．

#### index.html

```
{% for p in photo_list %}
    <div>
        <img src="{{ p.photo_thumbnail.url }}">
    </div>
{% endfor %}

```

これだけです．
`$ python manage.py runserver`して，`http://127.0.0.1:8000/`にアクセスしてみましょう．


## 改良2

現在画像は全て左端によっていると思います．このままでは，寂しいので簡易に見た目を整えてみます．

`photos/static/photos/index.css`を作成します．

#### index.css

```
body {
  background-color: #fafafa;
}

.main {
  width: 818px;
  margin: 0 auto;
}

header {
  overflow: hidden;
  margin: 16px auto;
}

header h1 {
  float: left;
  margin: 0;
}

header .header-nav {
  float: right;
}

header a {
  float: left;
  color: black;
  text-align: center;
  padding: 8px 16px;
  text-decoration: none;
  font-size: 16px;
}

.grid-container {
  display: grid;
  grid-gap: 16px;
  grid-template-columns: 1fr 1fr 1fr;
}

.grid-item {
  border: 1px solid #e6e6e6;
  width: 260px;
  height: 260px;
}

```

`{% load static %} <link  ... href="{% static 'photos/index.css' %}>`の部分で先程作成した`index.css`を読み込んでいます．

#### index.html

```
<!DOCTYPE html>
<html lang="ja">
<head>
    {% load static %}
    <link rel="stylesheet" type="text/css" href="{% static 'photos/index.css' %}">
    <title>Photos</title>
</head>
<body>
    <div class="main">
        <header>
            <h1>Photos</h1>
            <div class="header-nav">
                <a href="{% url 'form' %}">投稿</a>
            </div>
        </header>
        <div class="grid-container">
            {% for p in photo_list%}
                <div class="grid-item">
                    <img src="{{ p.photo_thumbnail.url }}">
                </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
```

`$ python manage.py runserver`して，`http://127.0.0.1:8000/`にアクセスしてみましょう．
