---
title: Build Small Idea Forge
emoji: 🛠️
colorFrom: green
colorTo: indigo
sdk: gradio
sdk_version: 5.34.0
app_file: app.py
pinned: false
tags:
  - build-small-hackathon
  - gradio
  - backyard-ai
  - thousand-token-wood
  - best-agent
  - best-demo
  - codex
---

# Build Small Idea Forge

A simple project-idea generator for the Hugging Face × Gradio **Build Small** hackathon.

The goal is to help a solo builder create as many small, shippable hackathon projects as possible. It reads the hackathon constraints into the app prompt and returns practical or whimsical project ideas with a suggested model, basic Gradio UI, MVP plan, demo hook, and README tags.

## Why it fits Build Small

- Uses a default text model under the 32B total-parameter cap: `Qwen/Qwen2.5-14B-Instruct`.
- Ships as a Gradio app.
- Keeps the implementation intentionally basic so it can be copied into a Hugging Face Space directly.
- Includes an offline deterministic fallback so the Space still produces ideas if no token or provider is available.


## Proje işleyişi - basit Türkçe özet

Bu proje bir **hackathon fikir üretici** uygulamasıdır. Amaç, Hugging Face Build Small hackathonu için hızlıca çok sayıda küçük ve yapılabilir proje fikri üretmektir.

### 1. Kullanıcı ne istediğini yazar

Uygulamada ilk kutuya ne tür projeler yapmak istediğini yazarsın. Örneğin öğrenci araçları, komik oyunlar, belge yardımcıları veya mahalle için küçük uygulamalar yazabilirsin.

### 2. Hackathon kategorisi seçilir

İki ana kategori vardır:

- **Backyard AI:** Günlük hayatta işe yarayan pratik yapay zeka projeleri.
- **Thousand Token Wood:** Daha eğlenceli, yaratıcı ve tuhaf yapay zeka projeleri.

### 3. Seviye ve kaynaklar seçilir

Uygulama senden seviyeni ve kullanacağın kaynakları seçmeni ister. Hugging Face kredileri, Zero GPU, Modal kredileri veya 4B altı model denemesi gibi seçenekler vardır.

### 4. Uygulama fikir üretir

Butona basınca uygulama önce `HF_TOKEN` var mı diye bakar. Token varsa Hugging Face üzerinden seçilen modeli çağırır. Varsayılan model `Qwen/Qwen2.5-14B-Instruct` modelidir ve 32B sınırının altındadır.

### 5. Token yoksa da çalışır

Eğer token yoksa veya model çağrısı hata verirse uygulama durmaz. İçindeki basit yedek fikir üreticiyi kullanır ve yine proje fikirleri verir.

### 6. Her fikirde ne çıkar?

Her proje fikri şu bilgileri içerir:

- Kısa proje adı
- Tek cümlelik açıklama
- Neden hackathona uygun olduğu
- Kullanılabilecek 32B altı model önerisi
- Basit Gradio arayüz planı
- Minimum yapılabilir ürün dosyaları
- Kısa demo videosu fikri

### 7. Hugging Face Space olarak nasıl kullanılır?

Bu depodaki üç dosya doğrudan Hugging Face Space içine koyulabilir:

- `app.py`: Uygulamanın ana kodu.
- `requirements.txt`: Gerekli Python paketleri.
- `README.md`: Space bilgileri ve açıklama dosyası.

Kısaca bu proje, başka hackathon projeleri bulmak için yapılmış küçük bir hackathon projesidir.

## How to run on Hugging Face Spaces

1. Create a Gradio Space in the `build-small-hackathon` organization.
2. Upload `app.py`, `requirements.txt`, and this `README.md`.
3. Add a Space secret named `HF_TOKEN` if you want live model generation.
4. Optionally set `MODEL_ID` to another under-32B chat model.

## Demo and social links

- Demo video: TODO
- Social post: TODO

## Tech

- Gradio UI
- `huggingface_hub.InferenceClient`
- Default model: `Qwen/Qwen2.5-14B-Instruct`
- Offline fallback idea generator
