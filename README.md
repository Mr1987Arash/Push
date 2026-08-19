# live-stream-wave-control (Push)

این مخزن یک scaffold اولیه برای پروژهٔ "Live Stream + Wave Control" است. هدف: یک سرویس پایتون برای دریافت نمونه‌های SDR (یا شبیه‌سازی)، تولید اسپکتروگرام/واترفال لحظه‌ای و ارسال آن به یک وب‑UI. همچنین شامل نکات مربوط به استریم و RTMP و یک اسکلت اندروید برای استریم و overlay است.

نکات مهم و هشدارها
- این پروژه برای "مشاهده و تحلیل" سیگنال‌ها (passive reception) طراحی شده است. هرگونه ارسال/جهت‌دهی رادیویی یا استفاده از فرستنده‌ها باید مطابق قوانین محل شما و با مجوز انجام شود.
- برای کار با SDR واقعی به سخت‌افزار (مثل RTL‑SDR) و درایورهای مناسب نیاز دارید.

Quick start (local, Linux / Raspberry Pi)
1. نصب پیش‌نیازها (سیستم):
   - نصب Python 3.10+
   - نصب ffmpeg (برای relay و ضبط)
   - نصب کتابخانه‌های SoapySDR/pyrtlsdr طبق docs اگر از سخت‌افزار استفاده می‌کنید

2. راه‌اندازی محیط پایتون:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt

3. اجرای سرور:

   cd backend
   ./run_server.sh

4. باز کردن UI:
   در مرورگر باز کنید: http://localhost:8000/ui

فایل‌های مهم
- backend/: کد FastAPI، reader برای SDR، و utils اسپکتروگرام
- ui/: وب‑UI ساده برای نمایش واترفال
- android/: اسکلت اندروید (مستندات و نمونه)
- scripts/: اسکریپت‌های کمک

برای جزئیات بیشتر فایل README هر بخش را ببینید.
