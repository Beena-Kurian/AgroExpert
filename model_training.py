# model_training.py
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
import os
import shutil
from datetime import datetime
from db import create_connection

class ModelTrainer:
    def __init__(self):
        self.model = None
        self.history = None
        self.class_names = None
        self.train_ds = None
        self.test_ds = None

    def prepare_dataset(self, base_path, new_disease_path=None, image_size=(224, 224), batch_size=64):
        """
        Prepare dataset from existing classes and optionally add new disease classes
        """
        # If new disease path is provided, first copy those images to base path
        if new_disease_path:
            for disease_folder in os.listdir(new_disease_path):
                src_path = os.path.join(new_disease_path, disease_folder)
                dst_path = os.path.join(base_path, disease_folder)
                if os.path.isdir(src_path):
                    if not os.path.exists(dst_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        # If folder exists, copy only the files
                        for file in os.listdir(src_path):
                            shutil.copy2(
                                os.path.join(src_path, file),
                                os.path.join(dst_path, file)
                            )

        # Get updated class names
        self.class_names = sorted(os.listdir(base_path))
        print(f"Total number of classes: {len(self.class_names)}")
        print("Classes:", self.class_names)

        # Create datasets
        self.train_ds = tf.keras.utils.image_dataset_from_directory(
            base_path,
            image_size=image_size,
            batch_size=batch_size,
            seed=500,
            validation_split=0.2,
            subset='training',
            shuffle=True,
            class_names=self.class_names
        )

        self.test_ds = tf.keras.utils.image_dataset_from_directory(
            base_path,
            image_size=image_size,
            batch_size=batch_size,
            seed=500,
            validation_split=0.2,
            subset='validation',
            shuffle=False,
            class_names=self.class_names
        )

        # Prefetch datasets
        self.train_ds = self.train_ds.prefetch(tf.data.AUTOTUNE)
        self.test_ds = self.test_ds.prefetch(tf.data.AUTOTUNE)

    def build_model(self, num_classes, conv_layers=5, dense_layers=[512, 128, 64]):
        """
        Build the CNN model with configurable parameters
        """
        model = keras.Sequential()
        model.add(keras.layers.Rescaling(scale=1/255, input_shape=(224, 224, 3)))

        # Add convolutional layers
        filters = 32
        for _ in range(conv_layers):
            model.add(keras.layers.Conv2D(filters, (3,3), activation='relu'))
            model.add(keras.layers.MaxPool2D((2,2)))
            model.add(keras.layers.Dropout(0.2))
            filters = min(filters * 2, 128)  # Double filters up to 128

        # Add dense layers
        model.add(keras.layers.Flatten())
        for units in dense_layers:
            model.add(keras.layers.Dense(units, activation='relu'))
            model.add(keras.layers.Dropout(0.2))

        # Output layer
        model.add(keras.layers.Dense(num_classes, activation='softmax'))

        self.model = model
        return model


    def train_model(self, epochs=15, learning_rate=0.001):
        """
        Train the model with specified parameters
        """
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        self.history = self.model.fit(
            self.train_ds,
            epochs=epochs,
            validation_data=self.test_ds
        )

        return self.history

    def evaluate_model(self):
        """
        Evaluate model and return test accuracy
        """
        test_loss, test_accuracy = self.model.evaluate(self.test_ds)
        return test_accuracy

    def plot_training_results(self):
        """
        Plot training history and save plots
        """
        # Create plots directory if it doesn't exist
        if not os.path.exists('plots'):
            os.makedirs('plots')

        # Training vs Validation Accuracy
        plt.figure(figsize=(10, 6))
        plt.plot(self.history.history['accuracy'], label='Training Accuracy')
        plt.plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.savefig('plots/accuracy_plot.png')
        plt.close()

        # Training vs Validation Loss
        plt.figure(figsize=(10, 6))
        plt.plot(self.history.history['loss'], label='Training Loss')
        plt.plot(self.history.history['val_loss'], label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig('plots/loss_plot.png')
        plt.close()

        return 'plots/accuracy_plot.png', 'plots/loss_plot.png'

    def save_model(self, version_number, description):
        """
        Save model with version information
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_filename = f"model_v{version_number}_{timestamp}.h5"
        model_path = os.path.join('models', model_filename)
        
        if not os.path.exists('models'):
            os.makedirs('models')
            
        self.model.save(model_path)
        return model_path
