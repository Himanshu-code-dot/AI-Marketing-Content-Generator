import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GRU, Dense, Dropout
import pickle
import os

data = pd.read_csv("data/dataset.csv")
texts = data["text"].tolist()

print(f"Loaded {len(texts)} lines from dataset.")

tokenizer = Tokenizer()
tokenizer.fit_on_texts(texts)

vocab_size = len(tokenizer.word_index) + 1
print(f"Vocabulary size: {vocab_size}")

sequences = []
for line in texts:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        sequences.append(token_list[:i + 1])

print(f"Total training sequences: {len(sequences)}")

max_len = max(len(x) for x in sequences)
sequences = pad_sequences(sequences, maxlen=max_len, padding='pre')

X = sequences[:, :-1]
y = sequences[:, -1]

y = tf.keras.utils.to_categorical(y, num_classes=vocab_size)

model = Sequential([
    Embedding(vocab_size, 64, input_length=max_len - 1),
    GRU(128, return_sequences=True),   
    Dropout(0.2),
    GRU(100),                         
    Dropout(0.2),
    Dense(vocab_size, activation='softmax')
])

model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

model.summary()

history = model.fit(
    X, y,
    epochs=100,
    batch_size=64,
    verbose=1,
)

os.makedirs("backend/model", exist_ok=True)

model.save("backend/model/gru_model.h5")

with open("backend/model/tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

with open("backend/model/max_len.pkl", "wb") as f:
    pickle.dump(max_len, f)

print("GRU model trained and saved to backend/model/")
