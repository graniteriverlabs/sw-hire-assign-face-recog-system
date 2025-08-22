import os
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
import pickle

DATA_DIR = 'data/faces'
MODEL_PATH = 'models/cnn_face_model.h5'
ENCODER_PATH = 'models/label_encoder.pkl'
IMG_SIZE = (160, 160)

# Load images and labels
images, labels = [], []

for person in os.listdir(DATA_DIR):
    person_dir = os.path.join(DATA_DIR, person)
    if not os.path.isdir(person_dir):
        continue
    for img_file in os.listdir(person_dir):
        if img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
            img_path = os.path.join(person_dir, img_file)
            img = np.array(layers.preprocessing.image.load_img(img_path, target_size=IMG_SIZE))
            images.append(img / 255.0)
            labels.append(person)

images = np.array(images)
labels = np.array(labels)

# Encode labels
le = LabelEncoder()
y = le.fit_transform(labels)
y = to_categorical(y)

# Save label encoder
os.makedirs('models', exist_ok=True)
with open(ENCODER_PATH, 'wb') as f:
    pickle.dump(le, f)

# Build CNN model
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3)),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(y.shape[1], activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Data augmentation
datagen = ImageDataGenerator(rotation_range=20,
                             zoom_range=0.2,
                             horizontal_flip=True,
                             validation_split=0.2)

train_gen = datagen.flow(images, y, batch_size=8, subset='training')
val_gen = datagen.flow(images, y, batch_size=8, subset='validation')

# Train model
model.fit(train_gen, validation_data=val_gen, epochs=30)
model.save(MODEL_PATH)
print(f"Model saved at {MODEL_PATH}")
