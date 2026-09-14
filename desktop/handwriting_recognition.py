import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageDraw
import tensorflow as tf
from io import BytesIO

class HandwritingRecognizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Handwritten Digit Recognition")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f0f0")

        # Initialize model with loading status
        self.result_label_temp = tk.Label(root, text="Loading model...", font=("Arial", 14))
        self.result_label_temp.pack(pady=20)
        self.root.update()

        # Load or create MNIST model
        self.model = self._get_or_create_model()

        # Remove loading label
        self.result_label_temp.pack_forget()

        # Create canvas for drawing
        self.canvas = tk.Canvas(
            root,
            width=280,
            height=280,
            bg="white",
            cursor="cross",
            relief=tk.RAISED,
            borderwidth=2
        )
        self.canvas.pack(pady=20)

        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Create PIL image for drawing
        self.image = Image.new("L", (280, 280), color=255)
        self.draw = ImageDraw.Draw(self.image)

        # Create buttons frame
        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(pady=10)

        # Recognize button
        recognize_btn = tk.Button(
            button_frame,
            text="Recognize",
            command=self._recognize,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        recognize_btn.pack(side=tk.LEFT, padx=5)

        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self._clear_canvas,
            bg="#f44336",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Result label
        self.result_label = tk.Label(
            root,
            text="Draw a digit (0-9) and click Recognize",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#333333"
        )
        self.result_label.pack(pady=10)

        # Prediction result frame
        result_frame = tk.Frame(root, bg="white", relief=tk.SUNKEN, borderwidth=2)
        result_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Prediction text
        self.prediction_label = tk.Label(
            result_frame,
            text="",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#4CAF50"
        )
        self.prediction_label.pack(pady=20)

        # Confidence text
        self.confidence_label = tk.Label(
            result_frame,
            text="",
            font=("Arial", 12),
            bg="white",
            fg="#666666"
        )
        self.confidence_label.pack(pady=5)

        # Drawing state
        self.last_x = 0
        self.last_y = 0

    def _get_or_create_model(self):
        """Load or create MNIST model"""
        import os

        model_path = "mnist_model.keras"

        # Check if model exists
        if os.path.exists(model_path):
            try:
                return tf.keras.models.load_model(model_path)
            except:
                pass

        # Create simple MNIST model
        print("Training MNIST model... This may take a minute.")
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

        # Train model with minimal output
        model.fit(x_train, y_train, epochs=5, batch_size=32, verbose=0)
        model.save(model_path)

        return model

    def _on_press(self, event):
        """Handle mouse press"""
        self.last_x = event.x
        self.last_y = event.y

    def _on_drag(self, event):
        """Handle mouse drag for drawing"""
        # Draw on canvas
        self.canvas.create_line(
            self.last_x, self.last_y,
            event.x, event.y,
            fill="black",
            width=5,
            capstyle=tk.ROUND,
            smooth=True
        )

        # Draw on PIL image
        self.draw.line(
            [(self.last_x, self.last_y), (event.x, event.y)],
            fill=0,
            width=5
        )

        self.last_x = event.x
        self.last_y = event.y

    def _on_release(self, event):
        """Handle mouse release"""
        pass

    def _clear_canvas(self):
        """Clear the canvas"""
        self.canvas.delete("all")
        self.image = Image.new("L", (280, 280), color=255)
        self.draw = ImageDraw.Draw(self.image)
        self.result_label.config(text="Draw a digit (0-9) and click Recognize")
        self.prediction_label.config(text="")
        self.confidence_label.config(text="")

    def _recognize(self):
        """Recognize the drawn digit"""
        # Convert PIL image to numpy array
        img_array = np.array(self.image)

        # Invert colors (white background to black)
        img_array = 255 - img_array

        # Normalize
        img_array = img_array.astype("float32") / 255.0

        # Resize to 28x28 (MNIST standard)
        img_resized = Image.fromarray((img_array * 255).astype("uint8")).resize((28, 28))
        img_data = np.array(img_resized).astype("float32") / 255.0

        # Flatten
        img_flat = img_data.reshape(1, 784)

        # Make prediction
        prediction = self.model.predict(img_flat, verbose=0)
        predicted_digit = np.argmax(prediction[0])
        confidence = np.max(prediction[0]) * 100

        # Update labels
        self.result_label.config(
            text=f"Recognized Digit",
            fg="#4CAF50"
        )
        self.prediction_label.config(text=str(predicted_digit))
        self.confidence_label.config(text=f"Confidence: {confidence:.2f}%")


if __name__ == "__main__":
    root = tk.Tk()
    app = HandwritingRecognizer(root)
    root.mainloop()
