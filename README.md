# SignDetector

Real-time American Sign Language recognition in the browser. Built at York University's **CTRL+HACK+DEL** hackathon.

The browser streams webcam frames to a local Flask service, which isolates the hand with MediaPipe, classifies the sign with a trained CNN, and sends back both an annotated frame and the predicted letter — all live, frame by frame.

---

## How it works

```
Browser (Next.js)                Flask server (:3001)
─────────────────                ────────────────────
webcam → <canvas>
  │ base64 JPEG
  └── POST /process-frame ──────► MediaPipe Hands
                                    │ landmarks → bounding box
                                    ├─ crop hand region
                                    ├─ resize 224×224, normalize
                                    └─ Keras CNN → argmax
      ◄── { image, prediction } ────┘
  annotated frame + letter
```

The prediction runs on a **skeleton-only** image: the frame is blanked to white and only the MediaPipe hand landmarks are drawn onto it, so the classifier sees hand geometry rather than skin tone, lighting, or background.

## Repository layout

| Path | What's in it |
| --- | --- |
| `acernity_ui/` | Next.js 15 + TypeScript frontend. Webcam capture, frame upload loop, and the result canvas live in `app/uicom.tsx`. Aceternity UI components (typewriter, sparkles, cover, gradient background) under `components/`. |
| `opencvdownloads/modelTrainingAndPrediction/` | The production Flask API (`testPort.py`), the training notebook (`signLanguageClassification.ipynb`), a batch prediction script (`predictionHandler.py`), and the trained model `lineASLClassifier.h5`. |
| `opencvdownloads/handonPort/production/` | Earlier hand-detection-only server plus `test_components/` — standalone experiments for camera reading, landmark drawing, and port handling. |

## The model

Trained in `signLanguageClassification.ipynb` on an ASL image dataset split 80/10/10 with `splitfolders`.

- **Architecture** — sequential CNN: four blocks of paired `Conv2D` layers (32 → 64 → 128 → 256 filters, 3×3, `same` padding) each followed by max pooling and dropout, then dense layers to a softmax head.
- **Training** — Adam, categorical cross-entropy, up to 30 epochs with `EarlyStopping` (patience 5, best weights restored) and `ReduceLROnPlateau` (patience 2).
- **Classes** — the notebook trains on 36 classes (`0–9`, `a–z`) at 200×200. The shipped `lineASLClassifier.h5` used by the live server is the landmark-image variant: **26 letters** at 224×224.

## Running it

**Prerequisites:** Python 3.12, Node 18+, and a webcam.

### 1. Backend

```bash
cd opencvdownloads/modelTrainingAndPrediction
pip install flask flask-cors opencv-python mediapipe tensorflow pillow numpy
python testPort.py
```

Serves on `0.0.0.0:3001` with CORS open to `http://localhost:3000`. Run it from this directory so `lineASLClassifier.h5` resolves.

### 2. Frontend

```bash
cd acernity_ui
npm install
npm run dev
```

Open `http://localhost:3000`, allow camera access, and start the feed. The client posts frames to `http://127.0.0.1:3001/process-frame` and renders the returned annotated image alongside the predicted letter.

## API

**`POST /process-frame`**

```jsonc
// request
{ "image": "data:image/jpeg;base64,<...>" }

// response
{
  "status": "frame processed successfully",
  "image": "data:image/png;base64,<annotated frame>",
  "prediction": "b"   // or "UNKNOWN" when no hand is detected
}
```

Detection uses `min_detection_confidence=0.8`. If MediaPipe finds no hand, the frame comes back annotated but the prediction is `UNKNOWN`.

## Known rough edges

This is hackathon code, and a few things are still hardcoded from the machines it was built on:

- `predictionHandler.py` points at a Windows test folder and loads `ASL_model.h5`, which isn't in the repo — it's a local batch-evaluation script, not part of the live pipeline.
- `testPort.py` opens a hardcoded `64stringimg.txt` path and a Windows `save_folder`; both are leftovers from debugging and unused by the request path.
- The bounding box is padded by 50px on each side without clamping to frame edges, so hands near the border can produce a bad crop.
