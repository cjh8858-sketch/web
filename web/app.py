import os
import numpy as np
from flask import Flask, render_template, request, jsonify
from PIL import Image
import tensorflow as tf
import io
import base64

app = Flask(__name__)

# Global model variable
model = None

def get_or_create_model():
    """Load or create MNIST model"""
    global model

    if model is not None:
        return model

    model_path = os.path.join(os.path.dirname(__file__), "mnist_model.keras")

    # Check if model exists
    if os.path.exists(model_path):
        try:
            model = tf.keras.models.load_model(model_path)
            print("Model loaded successfully")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")

    # Create and train new model
    print("Training MNIST model...")
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

    # Normalize data
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0

    # Flatten images
    x_train = x_train.reshape(-1, 784)
    x_test = x_test.reshape(-1, 784)

    # Create model
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation="relu", input_shape=(784,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    # Train model
    model.fit(x_train, y_train, epochs=5, batch_size=32, verbose=0)
    model.save(model_path)
    print("Model trained and saved")

    return model

def recognize_digit(canvas_image_data):
    """
    Process canvas image and recognize digit
    canvas_image_data: base64 encoded image from canvas
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(canvas_image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data))

        # Convert to grayscale
        image = image.convert('L')

        # Convert to numpy array
        img_array = np.array(image)

        # Invert colors
        img_array = 255 - img_array

        # Normalize
        img_array = img_array.astype("float32") / 255.0

        # Resize to 28x28
        img_resized = Image.fromarray((img_array * 255).astype("uint8")).resize((28, 28))
        img_data = np.array(img_resized).astype("float32") / 255.0

        # Flatten
        img_flat = img_data.reshape(1, 784)

        # Get model and make prediction
        model = get_or_create_model()
        prediction = model.predict(img_flat, verbose=0)
        predicted_digit = int(np.argmax(prediction[0]))
        confidence = float(np.max(prediction[0]) * 100)

        return {
            "digit": predicted_digit,
            "confidence": round(confidence, 2),
            "success": True
        }
    except Exception as e:
        print(f"Recognition error: {e}")
        return {
            "error": str(e),
            "success": False
        }

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    """API endpoint for digit recognition"""
    try:
        data = request.get_json()
        canvas_image = data.get('canvas')

        if not canvas_image:
            return jsonify({"error": "No image provided", "success": False}), 400

        result = recognize_digit(canvas_image)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Server is running"})

if __name__ == '__main__':
    # Load model on startup
    get_or_create_model()
    # Run Flask app
    app.run(debug=True, host='127.0.0.1', port=5000)
