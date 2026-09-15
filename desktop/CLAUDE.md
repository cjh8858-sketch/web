# CLAUDE.md - Desktop Version

This file provides guidance to Claude Code (claude.ai/code) when working with the desktop version of the Handwritten Digit Recognition application.

## Project Overview

The **Desktop Version** is a standalone Python application with a native GUI that recognizes handwritten digits (0-9). Built with Tkinter for cross-platform compatibility and compiled to a Windows executable for end-users who don't have Python installed.

## Architecture

The project consists of a single-file application with a Tkinter GUI and TensorFlow/Keras backend:

- **GUI (Tkinter)**: Canvas-based drawing interface with buttons for recognition and clearing
- **Model (TensorFlow/Keras)**: A 3-layer sequential neural network (128 → 64 → 10 neurons) trained on MNIST data
- **Image Processing (PIL)**: Handles canvas drawings, normalization, and resizing to 28x28 MNIST format
- **Prediction Pipeline**: Converts drawn image → inverts colors → resizes → flattens → predicts
- **Build System (PyInstaller)**: Compiles Python to standalone `.exe` executable

### Key Classes

- `HandwritingRecognizer`: Main application class handling GUI, model loading/training, and prediction logic
  - `_get_or_create_model()`: Loads saved model or trains a new one on first run (~1-2 minutes)
  - `_recognize()`: Processes canvas drawing and returns predicted digit + confidence
  - `_on_drag()`, `_on_press()`, `_on_release()`: Handle mouse drawing events
  - `_clear_canvas()`: Resets drawing area and prediction results

## Running the Application

### Option 1: Double-click Executable (Recommended)
```
Handwriting Recognition.exe
```
Located on Desktop or in `dist/` folder. Self-contained, no Python installation required.

### Option 2: Batch File
```
run_handwriting_recognizer.bat
```
Runs the Python script directly from desktop folder.

### Option 3: Python Script
```
python handwriting_recognition.py
```
Requires Python and dependencies installed (see below).

## Setup & Dependencies

### Install Dependencies
```
pip install tensorflow pillow numpy
```

For development or rebuilding the .exe:
```
pip install pyinstaller
```

### Model File
The trained MNIST model is saved as `mnist_model.keras` (~1.3 MB). On first run, the application trains the model (5 epochs) and saves it for faster subsequent launches.

## Building the Executable

Regenerate the `.exe` file if you modify the Python code (run from project root):

```
pyinstaller --onefile --windowed --name "Handwriting Recognition" desktop/handwriting_recognition.py
```

Output will be in `dist/Handwriting Recognition.exe`. Copy to Desktop or preferred location.

### PyInstaller Options Explained
- `--onefile`: Bundles everything into a single executable file
- `--windowed`: Removes console window (GUI-only application)
- `--name`: Sets executable name and window title

## Modifying the Application

### Improving Model Accuracy
- Increase `epochs` in `_get_or_create_model()` (currently 5, try 10-20)
- Adjust network architecture (add/remove layers or neurons in the Sequential model)
- The model trains on MNIST (60k samples), consider adding data augmentation for better robustness

### Extending UI
- Canvas dimensions are 280×280 (controlled in `__init__`)
- Prediction display uses Tkinter Labels; extend the result_frame for visualization
- Add sliders/buttons for model parameters by extending the button_frame
- Modify window geometry with `self.root.geometry("WIDTHxHEIGHT")`

### Custom Styling
- Button colors: Edit `bg="#4CAF50"` (hex color codes)
- Fonts: Modify font tuples like `font=("Arial", 14, "bold")`
- Canvas appearance: Change `bg="white"`, `cursor="cross"`, `borderwidth`, `relief`
- Window background: Edit `self.root.configure(bg="#f0f0f0")`

### Changing MNIST to Custom Dataset
- Replace `tf.keras.datasets.mnist.load_data()` with custom data loading
- Ensure input shape remains compatible with the model's input_shape=(784,)
- Retrain by deleting `mnist_model.keras` to trigger retraining on startup

## Common Tasks

### Clean Build
1. Delete `desktop/mnist_model.keras` to force model retraining on next run
2. Delete `build/` and `dist/` folders to clean PyInstaller artifacts before rebuilding

### Debug Model Performance
Add print statements in `_recognize()` after prediction:
```python
print("Prediction distribution:", prediction[0])
print("All digits:", {i: float(prediction[0][i]) for i in range(10)})
```

### Test Recognition
Draw digits slowly and deliberately. Digits similar in style to MNIST training data (printed/simple) are recognized more accurately than stylized handwriting.

### Add Logging
Import and configure logging at the top of `handwriting_recognition.py`:
```python
import logging
logging.basicConfig(
    filename='handwriting_recognition.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Distribute to Users
1. Build executable with PyInstaller
2. Create installer with NSIS or InnoSetup if needed
3. Include `mnist_model.keras` alongside `.exe` for faster first launch
4. Create shortcut on user's Desktop

## Directory Structure

```
desktop/
├── handwriting_recognition.py      # Main application (single-file)
├── run_handwriting_recognizer.bat  # Batch launcher for Python script
├── mnist_model.keras               # Trained model (generated on first run)
├── Handwriting Recognition.spec    # PyInstaller spec file (in parent)
├── build/                          # PyInstaller build directory (in parent)
├── dist/                           # Compiled executable output (in parent)
└── CLAUDE.md                       # This file
```

## Platform Considerations

### Windows
- Tkinter is pre-installed with Python on Windows
- TensorFlow CPU-only (GPU not available on native Windows)
- File paths use backslashes (handled automatically by Python)

### macOS/Linux
- May need to install Tkinter separately: `apt install python3-tk` or `brew install python-tk`
- TensorFlow works with CPU and GPU
- Executable building produces platform-specific binaries

## Notes

- First launch takes 1-2 minutes as the model trains; subsequent launches are instant
- The model uses CPU only (TensorFlow GPU not available on native Windows)
- Color inversion in `_recognize()` is critical: MNIST trains on black digits on white background, but the canvas draws white on white, so the image must be inverted before prediction
- Confidence scores represent softmax probabilities; 100% is rare; typical recognition shows 85-99% confidence for clear digits
- Tkinter is cross-platform but rendering behavior may differ slightly between OS
- PyInstaller creates large executables (~150-200 MB) due to bundled TensorFlow dependencies

## Troubleshooting

### "No module named 'tkinter'"
- Windows: Tkinter is included in standard Python installation
- macOS: `brew install python-tk`
- Linux: `apt install python3-tk`

### "CUDA not available"
- Expected on Windows; TensorFlow runs on CPU
- To enable GPU on Linux/macOS, install `tensorflow[and-cuda]`

### Executable won't run
- Try running from Command Prompt to see error messages
- Check Windows Defender isn't quarantining the file
- Ensure all dependencies are available (check PyInstaller warnings)

### Model training too slow
- Reduce `epochs` from 5 to 3 for faster training (less accurate)
- Reduce `batch_size` from 32 to 16 for quicker iterations
- Use smaller dataset if training MNIST replacement

## Performance Optimization

### Reduce Executable Size
- Use `--strip` flag with PyInstaller to remove debugging symbols
- Remove unused TensorFlow dependencies (requires manual configuration)

### Faster Model Loading
- Pre-convert model to TensorFlow Lite format (`.tflite`) for smaller size
- Consider ONNX export for cross-platform compatibility

### Parallel Processing
- Use `threading` to keep UI responsive during model prediction
- Wrap `_recognize()` in Thread to prevent GUI freezing
