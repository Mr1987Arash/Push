"""
Simple FastAPI backend that provides a WebSocket streaming FFT data (spectrum).
If an RTL-SDR device (pyrtlsdr) is available, it will use it; otherwise it falls back to simulated data.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import numpy as np
import base64
import json

try:
    from rtlsdr import RtlSdr
    HAS_RTLSDR = True
except Exception:
    HAS_RTLSDR = False

app = FastAPI()

@app.get("/api/status")
async def status():
    return {"status": "ok", "sdr": HAS_RTLSDR}

@app.get("/ui/")
async def ui_index():
    with open('ui/index.html', 'r', encoding='utf-8') as f:
        return HTMLResponse(f.read())

async def generate_spectrum_samples(center_freq=100e6, sample_rate=2.4e6, n_samples=1024):
    """Generator yielding PSD arrays."""
    if HAS_RTLSDR:
        sdr = RtlSdr()
        try:
            sdr.sample_rate = sample_rate
            sdr.center_freq = center_freq
            sdr.gain = 'auto'
            while True:
                samples = sdr.read_samples(n_samples)
                psd = np.abs(np.fft.fftshift(np.fft.fft(samples * np.hanning(len(samples)))))
                psd_db = 20 * np.log10(psd + 1e-12)
                # normalize
                arr = (psd_db - psd_db.min()) / (psd_db.ptp() + 1e-12)
                yield arr.tolist()
        finally:
            sdr.close()
    else:
        # simulated
        t = 0
        while True:
            x = np.linspace(0, 2*np.pi, n_samples)
            sig = 0.5*np.sin(5*x + t) + 0.3*np.sin(13*x + 2*t) + 0.2*np.random.randn(n_samples)
            psd = np.abs(np.fft.fftshift(np.fft.fft(sig * np.hanning(len(sig)))))
            psd_db = 20 * np.log10(psd + 1e-12)
            arr = (psd_db - psd_db.min()) / (psd_db.ptp() + 1e-12)
            t += 0.1
            await asyncio.sleep(0.1)
            yield arr.tolist()

@app.websocket("/ws/spectrum")
async def websocket_spectrum(ws: WebSocket):
    await ws.accept()
    gen = generate_spectrum_samples()
    try:
        while True:
            arr = await gen.__anext__()
            payload = json.dumps({"spectrum": arr})
            await ws.send_text(payload)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        return
    except StopAsyncIteration:
        return
