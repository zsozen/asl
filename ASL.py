# -*- coding: utf-8 -*-
"""16.08.2024ASLProject.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GYdOc5TMblcn_vZ_YXpUQo0ewO6--lDg

#Kütüphaneler ve Drive Bağlama
"""

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_absolute_error, mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from imblearn.over_sampling import SMOTE
from google.colab import files
from google.colab import drive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os

from google.colab import drive
drive.mount('/content/drive')

"""#Adım 1: Sign Language MNIST Veri Seti"""

import pandas as pd
import numpy as np

train_csv_path = '/truba/home/zsozen/sign_mnist_train.csv'
test_csv_path = '/truba/home/zsozen/sign_mnist_test.csv'

# CSV dosyalarını yüklenmesi
train_csv = pd.read_csv(train_csv_path)
test_csv = pd.read_csv(test_csv_path)

# Eğitim veri setinden özellikler ve etiketler
X_train_mnist = train_csv.drop('label', axis=1).values   # Özellikler
y_train_mnist = train_csv['label'].values                # Etiketler

# Test veri setinden özellikler ve etiketler
X_test_mnist = test_csv.drop('label', axis=1).values
y_test_mnist = test_csv['label'].values

# Görüntüleri yeniden şekillendirme (28x28 piksel)
X_train_mnist = X_train_mnist.reshape(-1, 28, 28, 1)
X_test_mnist = X_test_mnist.reshape(-1, 28, 28, 1)

print("Sign Language MNIST Eğitim veri seti şekli:", X_train_mnist.shape, y_train_mnist.shape)
print("Sign Language MNIST Test veri seti şekli:", X_test_mnist.shape, y_test_mnist.shape)

"""#Adım 2: ASL Alphabet Dataset Veri Seti"""

import os
import cv2

train_folder = '/truba/home/zsozen/ASLAlphabetDataset/asl_alphabet_train/'
test_folder = '/truba/home/zsozen/ASLAlphabetDataset/asl_alphabet_test/'

def load_images_from_folder(folder):
    images = []
    labels = []
    for label in os.listdir(folder):
        label_folder = os.path.join(folder, label)
        if os.path.isdir(label_folder):
            for filename in os.listdir(label_folder):
                img_path = os.path.join(label_folder, filename)
                img = cv2.imread(img_path)
                if img is not None:
                    img = cv2.resize(img, (28, 28))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    images.append(img)
                    labels.append(label)
    return np.array(images), np.array(labels)

# Eğitim ve test veri setlerini yükleme
X_train_alphabet, y_train_alphabet = load_images_from_folder(train_folder)
X_test_alphabet, y_test_alphabet = load_images_from_folder(test_folder)

# Görüntüleri yeniden şekillendirme
X_train_alphabet = X_train_alphabet.reshape(-1, 28, 28, 1)
X_test_alphabet = X_test_alphabet.reshape(-1, 28, 28, 1)

print("ASL Alphabet Dataset Eğitim veri seti şekli:", X_train_alphabet.shape, y_train_alphabet.shape)
print("ASL Alphabet Dataset Test veri seti şekli:", X_test_alphabet.shape, y_test_alphabet.shape)

"""#Adım 3: Etiket-Harf Eşleştirme Sözlüğü Oluşturma

"""

# Etiket-Harf Eşleştirme Sözlüğü
label_to_letter = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H',
    8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P',
    16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X',
    24: 'Y', 25: 'Z', 26: 'del', 27: 'nothing', 28: 'space'
}

letter_to_label = {v: k for k, v in label_to_letter.items()}

# Dataset etiketlerini dönüştürme
y_train_alphabet_numeric = np.array([letter_to_label[label] for label in y_train_alphabet])

print("Numeric Alphabet Labels:", np.unique(y_train_alphabet_numeric))

valid_indices = y_train_alphabet_numeric != -1
X_train_alphabet_filtered = X_train_alphabet[valid_indices]
y_train_alphabet_numeric = y_train_alphabet_numeric[valid_indices]

print("Filtered ASL Alphabet Dataset shapes:", X_train_alphabet_filtered.shape, y_train_alphabet_numeric.shape)

"""#Adım 4: Ortak Sınıfları Belirleme ve Filtreleme

---


"""

# Ortak sınıfları belirleme
common_classes = list(set(y_train_mnist) & set(y_train_alphabet_numeric))

print("Common classes:", common_classes)

# İlk veri setini (Sign Language MNIST) filtreleme
X_train_mnist_filtered = []
y_train_mnist_filtered = []
for i in range(len(y_train_mnist)):
    if y_train_mnist[i] in common_classes:
        X_train_mnist_filtered.append(X_train_mnist[i])
        y_train_mnist_filtered.append(y_train_mnist[i])

# İkinci veri setini (ASL Alphabet Dataset) filtreleme
X_train_alphabet_filtered = []
y_train_alphabet_filtered = []
for i in range(len(y_train_alphabet_numeric)):
    if y_train_alphabet_numeric[i] in common_classes:
        X_train_alphabet_filtered.append(X_train_alphabet[i])
        y_train_alphabet_filtered.append(y_train_alphabet_numeric[i])

# Numpy array'lerine çevirme
X_train_mnist_filtered = np.array(X_train_mnist_filtered)
y_train_mnist_filtered = np.array(y_train_mnist_filtered)
X_train_alphabet_filtered = np.array(X_train_alphabet_filtered)
y_train_alphabet_filtered = np.array(y_train_alphabet_filtered)

print("Filtered Sign Language MNIST shapes:", X_train_mnist_filtered.shape, y_train_mnist_filtered.shape)
print("Filtered ASL Alphabet Dataset shapes:", X_train_alphabet_filtered.shape, y_train_alphabet_filtered.shape)

"""#Adım 5: Veri Setlerini Birleştirme"""

# Veri setlerini birleştirme
X_combined_train = np.concatenate((X_train_mnist_filtered, X_train_alphabet_filtered), axis=0)
y_combined_train = np.concatenate((y_train_mnist_filtered, y_train_alphabet_filtered), axis=0)

print("Combined training data shape:", X_combined_train.shape)
print("Combined training labels shape:", y_combined_train.shape)

# Birleştirilmiş veri setini Google Drive'a kaydetme
save_path = '/content/drive/MyDrive/IndırgenmısVeri/combined_dataset.npz'

np.savez(save_path, X_combined_train=X_combined_train, y_combined_train=y_combined_train)



import numpy as np
# Birleştirilmiş veri setini Google Drive’dan yükleyin
load_path = '/content/drive/MyDrive/IndırgenmısVeri/combined_dataset.npz'

data = np.load(load_path)
X_combined_train = data['X_combined_train']
y_combined_train = data['y_combined_train']

print("Birleştirilmiş veri seti Google Drive'dan yüklendi:", X_combined_train.shape, y_combined_train.shape)

"""# #Adım 6: Rastgele 16 Görüntüyü Görselleştirme  """

import matplotlib.pyplot as plt
import numpy as np

# Toplam veri setinden rastgele 16 indeks seçimi
random_indices = np.random.choice(range(len(y_combined_train)), size=16, replace=False)

# Rastgele 16 görüntüyü görselleştirme ve etiketleri harf olarak gösterme
plt.figure(figsize=(10, 10))
for i, idx in enumerate(random_indices):
    plt.subplot(4, 4, i+1)
    plt.imshow(X_combined_train[idx].reshape(28, 28), cmap='gray')
    plt.title(f'Label: {label_to_letter[y_combined_train[idx]]}')
    plt.axis('off')
plt.show()

"""#Adım 7: Hybrid Model-1 CNN + RF (Attention Layer)"""

pip install keras-tuner

from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_absolute_error, mean_squared_error
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Input, Dropout, Reshape
from tensorflow.keras.layers import Attention
from tensorflow.keras.layers import Layer
from kerastuner.tuners import RandomSearch

# Custom Attention Layer
class AttentionLayer(Layer):
    def __init__(self):
        super(AttentionLayer, self).__init__()
        self.attention = Attention()

    def call(self, inputs):
        q = inputs
        k = inputs
        v = inputs
        attn_output = self.attention([q, k, v])
        return attn_output

# CNN modelini tanımlama fonksiyonu (Keras Tuner için)
def build_cnn_model(hp):
    input_shape = (28, 28, 1)
    inputs = Input(shape=input_shape)

    x = Conv2D(filters=hp.Int('conv_1_filter', min_value=32, max_value=128, step=16),
               kernel_size=hp.Choice('conv_1_kernel', values=[3,5]),
               activation='relu')(inputs)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Dropout(rate=hp.Float('dropout_1_rate', min_value=0.2, max_value=0.5, step=0.1))(x)

    x = Conv2D(filters=hp.Int('conv_2_filter', min_value=32, max_value=128, step=16),
               kernel_size=hp.Choice('conv_2_kernel', values=[3,5]),
               activation='relu')(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Dropout(rate=hp.Float('dropout_2_rate', min_value=0.2, max_value=0.5, step=0.1))(x)

    x = Flatten()(x)

    # Tensoru 3D hale getirmek için yeniden şekillendirme
    x = Reshape((-1, x.shape[-1]))(x)  # Reshape işlemi ile tensor 3D hale geliyor (batch_size, sequence_length, feature_dim)

    # Attention Layer ekleniyor
    attn_output = AttentionLayer()(x)

    # Çıktıyı Flatten katmanı ile 2D hale getirme
    flattened_output = Flatten()(attn_output)

    model = Model(inputs=inputs, outputs=flattened_output)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# K-Fold Cross Validation ile Eğitim ve Test
kf = KFold(n_splits=5, shuffle=True, random_state=42)

accuracy_scores = []
f1_scores = []
precision_scores = []
recall_scores = []
mae_scores = []
mse_scores = []
rmse_scores = []
error_rates = []

for train_index, test_index in kf.split(X_combined_train):
    X_train_fold, X_test_fold = X_combined_train[train_index], X_combined_train[test_index]
    y_train_fold, y_test_fold = y_combined_train[train_index], y_combined_train[test_index]

    # CNN + Attention modelini eğitme
    tuner = RandomSearch(
        build_cnn_model,
        objective='val_accuracy',
        max_trials=20,  # Deneme sayısını artırarak daha iyi sonuçlar bulabilirsiniz
        executions_per_trial=2,  # Her deneme için eğitim sayısını artırarak sonuçları iyileştirebilirsiniz
        directory='keras_tuner',
        project_name='cnn_attention_tuning'
    )

    tuner.search(X_train_fold, y_train_fold, epochs=10, validation_split=0.2)

    # En iyi modeli seçme
    best_model = tuner.get_best_models(num_models=1)[0]

    # En iyi hyperparametreleri yazdırma
    best_hyperparameters = tuner.get_best_hyperparameters(num_trials=1)[0]
    print("En iyi hyperparametreler: ", best_hyperparameters.values)

    # En iyi CNN modelinden özellik çıkarma
    cnn_with_attention_model = best_model
    X_train_features = cnn_with_attention_model.predict(X_train_fold)

    # Random Forest modeli eğitme
    X_train_features_flat = X_train_features.reshape(X_train_features.shape[0], -1)
    rf_model = RandomForestClassifier(n_estimators=100)
    rf_model.fit(X_train_features_flat, y_train_fold)

    # Test veri setini değerlendirme
    X_test_features = cnn_with_attention_model.predict(X_test_fold)
    X_test_features_flat = X_test_features.reshape(X_test_features.shape[0], -1)
    y_pred_rf = rf_model.predict(X_test_features_flat)

    # Metriklerin hesaplanması
    accuracy_rf = accuracy_score(y_test_fold, y_pred_rf)
    f1_rf = f1_score(y_test_fold, y_pred_rf, average='weighted')
    precision_rf = precision_score(y_test_fold, y_pred_rf, average='weighted')
    recall_rf = recall_score(y_test_fold, y_pred_rf, average='weighted')
    mae_rf = mean_absolute_error(y_test_fold, y_pred_rf)
    mse_rf = mean_squared_error(y_test_fold, y_pred_rf)
    rmse_rf = np.sqrt(mse_rf)
    error_rate_rf = 1 - accuracy_rf

    accuracy_scores.append(accuracy_rf)
    f1_scores.append(f1_rf)
    precision_scores.append(precision_rf)
    recall_scores.append(recall_rf)
    mae_scores.append(mae_rf)
    mse_scores.append(mse_rf)
    rmse_scores.append(rmse_rf)
    error_rates.append(error_rate_rf)

# Sonuçların ortalamalarını hesapla
avg_accuracy = np.mean(accuracy_scores)
avg_f1 = np.mean(f1_scores)
avg_precision = np.mean(precision_scores)
avg_recall = np.mean(recall_scores)
avg_mae = np.mean(mae_scores)
avg_mse = np.mean(mse_scores)
avg_rmse = np.mean(rmse_scores)
avg_error_rate = np.mean(error_rates)

print(f'Average Accuracy: {avg_accuracy}')
print(f'Average F1 Score: {avg_f1}')
print(f'Average Precision: {avg_precision}')
print(f'Average Recall: {avg_recall}')
print(f'Average MAE: {avg_mae}')
print(f'Average MSE: {avg_mse}')
print(f'Average RMSE: {avg_rmse}')
print(f'Average Error Rate: {avg_error_rate}')

# En iyi modeli seçme
best_model = tuner.get_best_models(num_models=1)[0]

# En iyi hiperparametreleri alma
best_hyperparameters = tuner.get_best_hyperparameters(num_trials=1)[0]

print("En iyi hiperparametreler:")
for param in best_hyperparameters.values.keys():
    print(f"{param}: {best_hyperparameters.get(param)}")

"""#Adım8: Hybrid Model 2 - ViT (Vision Transformer) + SVM"""

import numpy as np

# Rastgele örnekleme fonksiyonu
def reduce_dataset(X, y, target_size=1000):
    indices = np.random.choice(len(X), size=target_size, replace=False)
    X_reduced = X[indices]
    y_reduced = y[indices]
    return X_reduced, y_reduced

# Veri setini indirgeme
X_combined_train_reduced, y_combined_train_reduced = reduce_dataset(X_combined_train, y_combined_train)
print("İndirgenmiş veri seti şekli:", X_combined_train_reduced.shape, y_combined_train_reduced.shape)

import gc
from tensorflow.keras import backend as K

# Modeli çalıştırmadan önce
K.clear_session()
gc.collect()

import tensorflow as tf
import tensorflow_hub as hub
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import KFold
import numpy as np

# Veri setini [0, 1] aralığına ölçeklendirme
X_combined_train_rescaled = X_combined_train_reduced / 255.0  # İndirgenmiş veri seti

# Vision Transformer Modelini TensorFlow Hub'dan yükleme
vit_model_url = "https://tfhub.dev/sayakpaul/vit_b16_fe/1"
vit_layer = hub.KerasLayer(vit_model_url, trainable=False)

# ViT modeline girdi olarak kullanılacak görüntü boyutları
input_shape = (224, 224, 3)

# K-Fold Cross Validation ile Eğitim ve Test
kf = KFold(n_splits=5, shuffle=True, random_state=42)

accuracy_scores = []
f1_scores = []
precision_scores = []
recall_scores = []
mae_scores = []
mse_scores = []
rmse_scores = []
error_rates = []

for train_index, test_index in kf.split(X_combined_train_rescaled):
    X_train_fold, X_test_fold = X_combined_train_rescaled[train_index], X_combined_train_rescaled[test_index]
    y_train_fold, y_test_fold = y_combined_train_reduced[train_index], y_combined_train_reduced[test_index]

    # Görüntüleri ViT giriş boyutlarına yeniden boyutlandırma ve 3 kanala genişletme
    X_train_fold_resized = tf.image.resize(X_train_fold, input_shape[:2])
    X_train_fold_resized = tf.image.grayscale_to_rgb(X_train_fold_resized)  # Grayscale'den RGB'ye dönüştürme

    X_test_fold_resized = tf.image.resize(X_test_fold, input_shape[:2])
    X_test_fold_resized = tf.image.grayscale_to_rgb(X_test_fold_resized)  # Grayscale'den RGB'ye dönüştürme

    # ViT modelinden özellik çıkarma
    X_train_features = vit_layer(X_train_fold_resized, training=False)
    X_test_features = vit_layer(X_test_fold_resized, training=False)

    # Özellikleri düzleştirme
    X_train_features_flat = tf.reshape(X_train_features, [X_train_features.shape[0], -1]).numpy()
    X_test_features_flat = tf.reshape(X_test_features, [X_test_features.shape[0], -1]).numpy()

    # SVM modeli eğitme
    svm_model = SVC(kernel='linear', probability=True)
    svm_model.fit(X_train_features_flat, y_train_fold)

    # Test veri setini değerlendirme
    y_pred_svm = svm_model.predict(X_test_features_flat)

    # Metriklerin hesaplanması
    accuracy_svm = accuracy_score(y_test_fold, y_pred_svm)
    f1_svm = f1_score(y_test_fold, y_pred_svm, average='weighted')
    precision_svm = precision_score(y_test_fold, y_pred_svm, average='weighted')
    recall_svm = recall_score(y_test_fold, y_pred_svm, average='weighted')
    mae_svm = mean_absolute_error(y_test_fold, y_pred_svm)
    mse_svm = mean_squared_error(y_test_fold, y_pred_svm)
    rmse_svm = np.sqrt(mse_svm)
    error_rate_svm = 1 - accuracy_svm

    accuracy_scores.append(accuracy_svm)
    f1_scores.append(f1_svm)
    precision_scores.append(precision_svm)
    recall_scores.append(recall_svm)
    mae_scores.append(mae_svm)
    mse_scores.append(mse_svm)
    rmse_scores.append(rmse_svm)
    error_rates.append(error_rate_svm)

# Sonuçların ortalamalarını hesapla
avg_accuracy = np.mean(accuracy_scores)
avg_f1 = np.mean(f1_scores)
avg_precision = np.mean(precision_scores)
avg_recall = np.mean(recall_scores)
avg_mae = np.mean(mae_scores)
avg_mse = np.mean(mse_scores)
avg_rmse = np.mean(rmse_scores)
avg_error_rate = np.mean(error_rates)

print(f'Average Accuracy: {avg_accuracy}')
print(f'Average F1 Score: {avg_f1}')
print(f'Average Precision: {avg_precision}')
print(f'Average Recall: {avg_recall}')
print(f'Average MAE: {avg_mae}')
print(f'Average MSE: {avg_mse}')
print(f'Average RMSE: {avg_rmse}')
print(f'Average Error Rate: {avg_error_rate}')

"""altaki indirgenmemiş"""

import tensorflow as tf
import tensorflow_hub as hub
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import KFold
import numpy as np

# Veri setini [0, 1] aralığına ölçeklendirme
X_combined_train_rescaled = X_combined_train / 255.0  # X_combined_train, birleştirilmiş veri seti

# Vision Transformer Modelini TensorFlow Hub'dan yükleme
vit_model_url = "https://tfhub.dev/sayakpaul/vit_b16_fe/1"
vit_layer = hub.KerasLayer(vit_model_url, trainable=False)

# ViT modeline girdi olarak kullanılacak görüntü boyutları
input_shape = (224, 224, 3)

# K-Fold Cross Validation ile Eğitim ve Test
kf = KFold(n_splits=5, shuffle=True, random_state=42)

accuracy_scores = []
f1_scores = []
precision_scores = []
recall_scores = []
mae_scores = []
mse_scores = []
rmse_scores = []
error_rates = []

for train_index, test_index in kf.split(X_combined_train_rescaled):
    X_train_fold, X_test_fold = X_combined_train_rescaled[train_index], X_combined_train_rescaled[test_index]
    y_train_fold, y_test_fold = y_combined_train[train_index], y_combined_train[test_index]

    # Görüntüleri ViT giriş boyutlarına yeniden boyutlandırma
    X_train_fold_resized = tf.image.resize(X_train_fold, input_shape[:2])
    X_test_fold_resized = tf.image.resize(X_test_fold, input_shape[:2])

    # ViT modelinden özellik çıkarma
    X_train_features = vit_layer(X_train_fold_resized)
    X_test_features = vit_layer(X_test_fold_resized)

    # Özellikleri düzleştirme
    X_train_features_flat = tf.reshape(X_train_features, [X_train_features.shape[0], -1]).numpy()
    X_test_features_flat = tf.reshape(X_test_features, [X_test_features.shape[0], -1]).numpy()

    # SVM modeli eğitme
    svm_model = SVC(kernel='linear', probability=True)
    svm_model.fit(X_train_features_flat, y_train_fold)

    # Test veri setini değerlendirme
    y_pred_svm = svm_model.predict(X_test_features_flat)

    # Metriklerin hesaplanması
    accuracy_svm = accuracy_score(y_test_fold, y_pred_svm)
    f1_svm = f1_score(y_test_fold, y_pred_svm, average='weighted')
    precision_svm = precision_score(y_test_fold, y_pred_svm, average='weighted')
    recall_svm = recall_score(y_test_fold, y_pred_svm, average='weighted')
    mae_svm = mean_absolute_error(y_test_fold, y_pred_svm)
    mse_svm = mean_squared_error(y_test_fold, y_pred_svm)
    rmse_svm = np.sqrt(mse_svm)
    error_rate_svm = 1 - accuracy_svm

    accuracy_scores.append(accuracy_svm)
    f1_scores.append(f1_svm)
    precision_scores.append(precision_svm)
    recall_scores.append(recall_svm)
    mae_scores.append(mae_svm)
    mse_scores.append(mse_svm)
    rmse_scores.append(rmse_svm)
    error_rates.append(error_rate_svm)

# Sonuçların ortalamalarını hesapla
avg_accuracy = np.mean(accuracy_scores)
avg_f1 = np.mean(f1_scores)
avg_precision = np.mean(precision_scores)
avg_recall = np.mean(recall_scores)
avg_mae = np.mean(mae_scores)
avg_mse = np.mean(mse_scores)
avg_rmse = np.mean(rmse_scores)
avg_error_rate = np.mean(error_rates)

print(f'Average Accuracy: {avg_accuracy}')
print(f'Average F1 Score: {avg_f1}')
print(f'Average Precision: {avg_precision}')
print(f'Average Recall: {avg_recall}')
print(f'Average MAE: {avg_mae}')
print(f'Average MSE: {avg_mse}')
print(f'Average RMSE: {avg_rmse}')
print(f'Average Error Rate: {avg_error_rate}')

"""#Adım 11: Ensemble Learning - Voting"""



import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_absolute_error, mean_squared_error

# CNN + RF (Attention Layer) ve ViT + SVM modellerinden test setine ait tahminleri alıyoruz

# Hybrid 1: CNN + RF modelinin test seti tahminleri
X_test_features_flat_cnn = cnn_with_attention_model.predict(X_combined_test).reshape(X_combined_test.shape[0], -1)
y_pred_rf = rf_model.predict(X_test_features_flat_cnn)

# Hybrid 2: ViT + SVM modelinin test seti tahminleri
X_combined_test_rescaled = X_combined_test / 255.0  # Test setini ölçeklendirme
X_test_fold_resized = tf.image.resize(X_combined_test_rescaled, input_shape[:2])  # ViT giriş boyutlarına yeniden boyutlandırma
X_test_features_flat_vit = tf.reshape(vit_layer(X_test_fold_resized), [X_combined_test.shape[0], -1]).numpy()
y_pred_svm = svm_model.predict(X_test_features_flat_vit)

# Ensemble Model: Her iki modelin tahminlerini birleştiriyoruz (ortalamasını alıyoruz)
ensemble_predictions = np.round((y_pred_rf + y_pred_svm) / 2).astype(int)

# Ensemble Model Performans Metriklerini Hesaplama
accuracy_ensemble = accuracy_score(y_combined_test, ensemble_predictions)
f1_ensemble = f1_score(y_combined_test, ensemble_predictions, average='weighted')
precision_ensemble = precision_score(y_combined_test, ensemble_predictions, average='weighted')
recall_ensemble = recall_score(y_combined_test, ensemble_predictions, average='weighted')
mae_ensemble = mean_absolute_error(y_combined_test, ensemble_predictions)
mse_ensemble = mean_squared_error(y_combined_test, ensemble_predictions)
rmse_ensemble = np.sqrt(mse_ensemble)
error_rate_ensemble = 1 - accuracy_ensemble

# Sonuçların Yazdırılması
print(f"Ensemble Model Accuracy: {accuracy_ensemble}")
print(f"F1 Score: {f1_ensemble}")
print(f"Precision: {precision_ensemble}")
print(f"Recall: {recall_ensemble}")
print(f"Mean Absolute Error (MAE): {mae_ensemble}")
print(f"Mean Squared Error (MSE): {mse_ensemble}")
print(f"Root Mean Squared Error (RMSE): {rmse_ensemble}")
print(f"Error Rate: {error_rate_ensemble}")

"""#Adım 11: Ensemble Learning - Stacking"""

from sklearn.ensemble import StackingClassifier

# Stacking Ensemble Model
stacking_model = StackingClassifier(
    estimators=[
        ('cnn_rf', cnn_rf_model),
        ('vit_svm', vit_svm_model)
    ],
    final_estimator=RandomForestClassifier()
)

# K-Fold Cross Validation ile Stacking Modeli
accuracy_scores_stacking = []
f1_scores_stacking = []
precision_scores_stacking = []
recall_scores_stacking = []
mae_scores_stacking = []
mse_scores_stacking = []
rmse_scores_stacking = []
error_rates_stacking = []

for train_index, test_index in kf.split(X_combined_train):
    X_train_fold, X_test_fold = X_combined_train[train_index], X_combined_train[test_index]
    y_train_fold, y_test_fold = y_combined_train[train_index], y_combined_train[test_index]

    # Stacking modelini eğitme
    stacking_model.fit(X_train_fold, y_train_fold)

    y_pred_stacking = stacking_model.predict(X_test_fold)

    accuracy_stacking = accuracy_score(y_test_fold, y_pred_stacking)
    f1_stacking = f1_score(y_test_fold, y_pred_stacking, average='weighted')
    precision_stacking = precision_score(y_test_fold, y_pred_stacking, average='weighted')
    recall_stacking = recall_score(y_test_fold, y_pred_stacking, average='weighted')
    mae_stacking = mean_absolute_error(y_test_fold, y_pred_stacking)
    mse_stacking = mean_squared_error(y_test_fold, y_pred_stacking)
    rmse_stacking = np.sqrt(mse_stacking)
    error_rate_stacking = 1 - accuracy_stacking

    accuracy_scores_stacking.append(accuracy_stacking)
    f1_scores_stacking.append(f1_stacking)
    precision_scores_stacking.append(precision_stacking)
    recall_scores_stacking.append(recall_stacking)
    mae_scores_stacking.append(mae_stacking)
    mse_scores_stacking.append(mse_stacking)
    rmse_scores_stacking.append(rmse_stacking)
    error_rates_stacking.append(error_rate_stacking)

# Sonuçların ortalamalarını hesaplama
avg_accuracy_stacking = np.mean(accuracy_scores_stacking)
avg_f1_stacking = np.mean(f1_scores_stacking)
avg_precision_stacking = np.mean(precision_scores_stacking)
avg_recall_stacking = np.mean(recall_scores_stacking)
avg_mae_stacking = np.mean(mae_scores_stacking)
avg_mse_stacking = np.mean(mse_scores_stacking)
avg_rmse_stacking = np.mean(rmse_scores_stacking)
avg_error_rate_stacking = np.mean(error_rates_stacking)

print(f'Stacking - Average Accuracy: {avg_accuracy_stacking}')
print(f'Stacking - Average F1 Score: {avg_f1_stacking}')
print(f'Stacking - Average Precision: {avg_precision_stacking}')
print(f'Stacking - Average Recall: {avg_recall_stacking}')
print(f'Stacking - Average MAE: {avg_mae_stacking}')
print(f'Stacking - Average MSE: {avg_mse_stacking}')
print(f'Stacking - Average RMSE: {avg_rmse_stacking}')
print(f'Stacking - Average Error Rate: {avg_error_rate_stacking}')

"""#Adım 11: Ensemble Learning - Ağırlıklı Ortalama"""

from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_absolute_error, mean_squared_error
import numpy as np

# Weighted Average Modeli eğitme ve değerlendirme
kf = KFold(n_splits=5, shuffle=True, random_state=42)

accuracy_scores_weighted = []
f1_scores_weighted = []
precision_scores_weighted = []
recall_scores_weighted = []
mae_scores_weighted = []
mse_scores_weighted = []
rmse_scores_weighted = []
error_rates_weighted = []

weights = [0.5, 0.5]  # Modellerin ağırlıkları

for train_index, test_index in kf.split(X_combined_train):
    X_train_fold, X_test_fold = X_combined_train[train_index], X_combined_train[test_index]
    y_train_fold, y_test_fold = y_combined_train[train_index], y_combined_train[test_index]

    # Modelleri eğitme
    cnn_rf_model.fit(X_train_fold, y_train_fold)
    vit_svm_model.fit(X_train_fold, y_train_fold)

    y_pred_cnn_rf = cnn_rf_model.predict_proba(X_test_fold)
    y_pred_vit_svm = vit_svm_model.predict_proba(X_test_fold)

    y_pred_weighted = (weights[0] * y_pred_cnn_rf) + (weights[1] * y_pred_vit_svm)
    y_pred_weighted = np.argmax(y_pred_weighted, axis=1)

    accuracy_weighted = accuracy_score(y_test_fold, y_pred_weighted)
    f1_weighted = f1_score(y_test_fold, y_pred_weighted, average='weighted')
    precision_weighted = precision_score(y_test_fold, y_pred_weighted, average='weighted')
    recall_weighted = recall_score(y_test_fold, y_pred_weighted, average='weighted')
    mae_weighted = mean_absolute_error(y_test_fold, y_pred_weighted)
    mse_weighted = mean_squared_error(y_test_fold, y_pred_weighted)
    rmse_weighted = np.sqrt(mse_weighted)
    error_rate_weighted = 1 - accuracy_weighted

    accuracy_scores_weighted.append(accuracy_weighted)
    f1_scores_weighted.append(f1_weighted)
    precision_scores_weighted.append(precision_weighted)
    recall_scores_weighted.append(recall_weighted)
    mae_scores_weighted.append(mae_weighted)
    mse_scores_weighted.append(mse_weighted)
    rmse_scores_weighted.append(rmse_weighted)
    error_rates_weighted.append(error_rate_weighted)

# Sonuçların ortalamalarını hesaplama
avg_accuracy_weighted = np.mean(accuracy_scores_weighted)
avg_f1_weighted = np.mean(f1_scores_weighted)
avg_precision_weighted = np.mean(precision_scores_weighted)
avg_recall_weighted = np.mean(recall_scores_weighted)
avg_mae_weighted = np.mean(mae_scores_weighted)
avg_mse_weighted = np.mean(mse_scores_weighted)
avg_rmse_weighted = np.mean(rmse_scores_weighted)
avg_error_rate_weighted = np.mean(error_rates_weighted)

print(f'Weighted - Average Accuracy: {avg_accuracy_weighted}')
print(f'Weighted - Average F1 Score: {avg_f1_weighted}')
print(f'Weighted - Average Precision: {avg_precision_weighted}')
print(f'Weighted - Average Recall: {avg_recall_weighted}')
print(f'Weighted - Average MAE: {avg_mae_weighted}')
print(f'Weighted - Average MSE: {avg_mse_weighted}')
print(f'Weighted - Average RMSE: {avg_rmse_weighted}')
print(f'Weighted - Average Error Rate: {avg_error_rate_weighted}')

"""#Sonuçlar"""

import pandas as pd

# Tüm modellerin sonuçlarını bir tabloya ekleme
results = {
    'Model': [],
    'Accuracy': [],
    'F1 Score': [],
    'Precision': [],
    'Recall': [],
    'MAE': [],
    'MSE': [],
    'RMSE': [],
    'Error Rate': []
}

# Model 1 sonuçları (CNN + RF)
results['Model'].append('CNN + RF')
results['Accuracy'].append(avg_accuracy_cnn_rf)
results['F1 Score'].append(avg_f1_cnn_rf)
results['Precision'].append(avg_precision_cnn_rf)
results['Recall'].append(avg_recall_cnn_rf)
results['MAE'].append(avg_mae_cnn_rf)
results['MSE'].append(avg_mse_cnn_rf)
results['RMSE'].append(avg_rmse_cnn_rf)
results['Error Rate'].append(avg_error_rate_cnn_rf)

# Model 2 sonuçları (ViT + SVM)
results['Model'].append('ViT + SVM')
results['Accuracy'].append(avg_accuracy_vit_svm)
results['F1 Score'].append(avg_f1_vit_svm)
results['Precision'].append(avg_precision_vit_svm)
results['Recall'].append(avg_recall_vit_svm)
results['MAE'].append(avg_mae_vit_svm)
results['MSE'].append(avg_mse_vit_svm)
results['RMSE'].append(avg_rmse_vit_svm)
results['Error Rate'].append(avg_error_rate_vit_svm)

# Ensemble Model 1 sonuçları (Voting Classifier)
results['Model'].append('Voting Classifier')
results['Accuracy'].append(avg_accuracy_voting)
results['F1 Score'].append(avg_f1_voting)
results['Precision'].append(avg_precision_voting)
results['Recall'].append(avg_recall_voting)
results['MAE'].append(avg_mae_voting)
results['MSE'].append(avg_mse_voting)
results['RMSE'].append(avg_rmse_voting)
results['Error Rate'].append(avg_error_rate_voting)

# Ensemble Model 2 sonuçları (Stacking Classifier)
results['Model'].append('Stacking Classifier')
results['Accuracy'].append(avg_accuracy_stacking)
results['F1 Score'].append(avg_f1_stacking)
results['Precision'].append(avg_precision_stacking)
results['Recall'].append(avg_recall_stacking)
results['MAE'].append(avg_mae_stacking)
results['MSE'].append(avg_mse_stacking)
results['RMSE'].append(avg_rmse_stacking)
results['Error Rate'].append(avg_error_rate_stacking)

# Ensemble Model 3 sonuçları (Weighted Average)
results['Model'].append('Weighted Average')
results['Accuracy'].append(avg_accuracy_weighted)
results['F1 Score'].append(avg_f1_weighted)
results['Precision'].append(avg_precision_weighted)
results['Recall'].append(avg_recall_weighted)
results['MAE'].append(avg_mae_weighted)
results['MSE'].append(avg_mse_weighted)
results['RMSE'].append(avg_rmse_weighted)
results['Error Rate'].append(avg_error_rate_weighted)

# Sonuçları DataFrame'e dönüştürme
results_df = pd.DataFrame(results)

# Sonuçları gösterme
print(results_df)

# Sonuçları CSV olarak kaydetme
results_df.to_csv('model_results.csv', index=False)

import ace_tools as tools; tools.display_dataframe_to_user(name="Model Results", dataframe=results_df)

def print_results_table(results):
    print("+--------------------+----------------+----------------+----------------+----------------+----------------+----------------+----------------+----------------+")
    print("| Model              | Accuracy       | F1 Score       | Precision      | Recall         | MAE            | MSE            | RMSE           | Error Rate     |")
    print("+--------------------+----------------+----------------+----------------+----------------+----------------+----------------+----------------+----------------+")
    for result in results:
        print("| {:<18} | {:<14} | {:<14} | {:<14} | {:<14} | {:<14} | {:<14} | {:<14} | {:<14} |".format(
            result['model'],
            f"{result['accuracy']:.4f}",
            f"{result['f1']:.4f}",
            f"{result['precision']:.4f}",
            f"{result['recall']:.4f}",
            f"{result['mae']:.4f}",
            f"{result['mse']:.4f}",
            f"{result['rmse']:.4f}",
            f"{result['error_rate']:.4f}"
        ))
    print("+--------------------+----------------+----------------+----------------+----------------+----------------+----------------+----------------+----------------+")

# Tüm sonuçları bir listeye ekleme
results = [
    {"model": "CNN + RF", "accuracy": avg_accuracy_cnn_rf, "f1": avg_f1_cnn_rf, "precision": avg_precision_cnn_rf, "recall": avg_recall_cnn_rf, "mae": avg_mae_cnn_rf, "mse": avg_mse_cnn_rf, "rmse": avg_rmse_cnn_rf, "error_rate": avg_error_rate_cnn_rf},
    {"model": "ViT + SVM", "accuracy": avg_accuracy_vit_svm, "f1": avg_f1_vit_svm, "precision": avg_precision_vit_svm, "recall": avg_recall_vit_svm, "mae": avg_mae_vit_svm, "mse": avg_mse_vit_svm, "rmse": avg_rmse_vit_svm, "error_rate": avg_error_rate_vit_svm},
    {"model": "Voting Ensemble", "accuracy": accuracy_voting, "f1": f1_voting, "precision": precision_voting, "recall": recall_voting, "mae": mae_voting, "mse": mse_voting, "rmse": rmse_voting, "error_rate": error_rate_voting},
    {"model": "Stacking Ensemble", "accuracy": accuracy_stacking, "f1": f1_stacking, "precision": precision_stacking, "recall": recall_stacking, "mae": mae_stacking, "mse": mse_stacking, "rmse": rmse_stacking, "error_rate": error_rate_stacking},
    {"model": "Weighted Avg Ensemble", "accuracy": accuracy_weighted, "f1": f1_weighted, "precision": precision_weighted, "recall": recall_weighted, "mae": mae_weighted, "mse": mse_weighted, "rmse": rmse_weighted, "error_rate": error_rate_weighted}
]

print_results_table(results)
