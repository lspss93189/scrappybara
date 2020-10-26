import numpy as np
import tensorflow as tf

import scrappybara.config as cfg
from scrappybara.syntax.dependencies import NB_DEPS
from scrappybara.syntax.tags import NB_TAGS
from scrappybara.syntax.transitions import Trans
from scrappybara.utils.files import file_path


class _SentenceModel(object):

    def __init__(self):
        # Chars CNN
        self.__char_vector_size = 100
        self.__convolution_filters = 128
        # Word features
        self._nb_tags = NB_TAGS
        self._nb_deps = NB_DEPS
        self._tag_vector_size = 20
        self._dep_vector_size = 40
        # LSTM
        self._lstm_dropout = 0.2
        # Model
        self._model = None

    def _char_model(self, charset_size):
        """We use a CNN for syllables of 2, 3, 4 & 5 characters to extract morphological features of a word.
        Words are minimum 3 characters-long because of the padding.
        """
        char_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH, cfg.PADDED_WORD_LENGTH),
                                            dtype=tf.int32)
        char_embed = tf.keras.layers.Embedding(charset_size, self.__char_vector_size, mask_zero=True)(char_inputs)
        windows = [2, 3, 4, 5]
        pools = []
        for window in windows:
            conv = tf.keras.layers.Conv2D(self.__convolution_filters, (1, window), activation='relu', padding='same')(
                char_embed)
            pools.append(tf.keras.layers.MaxPool2D(pool_size=(1, cfg.PADDED_WORD_LENGTH))(conv))
        concat_cnns = tf.keras.layers.concatenate(pools, axis=2)
        cnn = tf.keras.layers.Reshape((cfg.PADDED_SENT_LENGTH, self.__convolution_filters * len(windows)))(
            concat_cnns)
        return tf.keras.Model(inputs=char_inputs, outputs=cnn)

    def _learn(self, batch_size, patience, epochs, train_y, validation_split, *args):
        if validation_split:
            metric = 'val_accuracy'
        else:
            metric = 'accuracy'
        callback = tf.keras.callbacks.EarlyStopping(monitor=metric, mode='max', patience=patience,
                                                    restore_best_weights=True)
        history = self._model.fit([np.array(arg) for arg in args], np.array(train_y), validation_split=validation_split,
                                  batch_size=batch_size, epochs=epochs, callbacks=[callback])
        return max(history.history[metric]) * 100

    def _save(self, filename):
        self._model.save_weights(file_path('data/models', filename))

    def _load(self, filename):
        self._model.load_weights(file_path('data/models', filename))


class PTagsModel(_SentenceModel):
    """Predicts part-of-speech tags for every token in a sentence"""

    def __init__(self, charset_size):
        super().__init__()
        self.__filename = 'ptags_weights.h5'
        # Params
        lstm_units = 512
        # Char model
        char_model = self._char_model(charset_size)
        # Word model
        word_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH, cfg.WORD_VECTOR_SIZE),
                                            dtype=tf.float32)
        word_repr = tf.keras.layers.concatenate([char_model.output, word_inputs], axis=2)
        word_model = tf.keras.Model(inputs=[char_model.input, word_inputs], outputs=word_repr)
        # Model
        mask = tf.keras.layers.Masking(mask_value=0.0).compute_mask(word_model.output)
        bilstm = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(
            lstm_units, return_sequences=True, dropout=self._lstm_dropout))(word_model.output, mask=mask)
        probas = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(self._nb_tags, activation='softmax'))(bilstm)
        self._model = tf.keras.Model(inputs=word_model.inputs, outputs=probas)
        self._model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def learn(self, batch_size, patience, epochs, train_y, validation_split, train_char_ids, train_word_vectors):
        return self._learn(batch_size, patience, epochs, train_y, validation_split, train_char_ids, train_word_vectors)

    def save(self):
        self._save(self.__filename)

    def load(self):
        self._load(self.__filename)
        return self

    def predict(self, char_codes, word_vectors):
        seqs = self._model.predict([np.array(char_codes), np.array(word_vectors)])
        return [[np.argmax(probas) for probas in seq] for seq in seqs]


class PDepsModel(_SentenceModel):
    """Predicts parent dependencies for every token in a sentence"""

    def __init__(self, charset_size):
        super().__init__()
        self.__filename = 'pdeps_weights.h5'
        # Params
        lstm_units = 512
        # Char model
        char_model = self._char_model(charset_size)
        # Word model
        tag_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH,), dtype=tf.int32)
        word_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH, cfg.WORD_VECTOR_SIZE),
                                            dtype=tf.float32)
        tag_embed = tf.keras.layers.Embedding(self._nb_tags, self._tag_vector_size)(tag_inputs)
        word_repr = tf.keras.layers.concatenate([char_model.output, word_inputs, tag_embed], axis=2)
        word_model = tf.keras.Model(inputs=[tag_inputs, char_model.input, word_inputs], outputs=word_repr)
        # Model
        mask = tf.keras.layers.Masking(mask_value=0.0).compute_mask(word_model.output)
        bilstm = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(
            lstm_units, return_sequences=True, dropout=self._lstm_dropout))(word_model.output, mask=mask)
        probas = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(self._nb_deps, activation='softmax'))(bilstm)
        self._model = tf.keras.Model(inputs=word_model.inputs, outputs=probas)
        self._model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def learn(self, batch_size, patience, epochs, train_y, validation_split, train_tag_ids, train_char_ids,
              train_word_vectors):
        return self._learn(batch_size, patience, epochs, train_y, validation_split, train_tag_ids, train_char_ids,
                           train_word_vectors)

    def save(self):
        self._save(self.__filename)

    def load(self):
        self._load(self.__filename)
        return self

    def predict(self, tag_codes, char_codes, word_vectors):
        seqs = self._model.predict([np.array(tag_codes), np.array(char_codes), np.array(word_vectors)])
        return [[np.argmax(probas) for probas in seq] for seq in seqs]


class TransModel(_SentenceModel):
    """Predicts parsing transition"""

    def __init__(self, charset_size):
        super().__init__()
        self.__filename = 'trans_weights.h5'
        # Params
        lstm_units = 512
        mlp_units = 512
        mlp_dropout = 0.5
        trans_size = len([trans for trans in Trans])
        # Char model
        char_model = self._char_model(charset_size)
        # Word model
        tag_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH,), dtype=tf.int32)
        dep_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH,), dtype=tf.int32)
        word_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH, cfg.WORD_VECTOR_SIZE),
                                            dtype=tf.float32)
        masks_1_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH,), dtype=tf.bool)
        masks_2_inputs = tf.keras.layers.Input(shape=(cfg.PADDED_SENT_LENGTH,), dtype=tf.bool)
        tag_embed = tf.keras.layers.Embedding(self._nb_tags, self._tag_vector_size)(tag_inputs)
        dep_embed = tf.keras.layers.Embedding(self._nb_deps, self._dep_vector_size)(dep_inputs)
        word_repr = tf.keras.layers.concatenate([char_model.output, word_inputs, tag_embed, dep_embed], axis=2)
        word_model = tf.keras.Model(inputs=[tag_inputs, dep_inputs, char_model.input, word_inputs], outputs=word_repr)
        # BiLstm model
        mask = tf.keras.layers.Masking(mask_value=0.0).compute_mask(word_model.output)
        bilstm = tf.keras.layers.Bidirectional(
            tf.keras.layers.LSTM(lstm_units, return_sequences=True, dropout=self._lstm_dropout))(
            word_model.output, mask=mask)
        timestep1 = tf.boolean_mask(bilstm, masks_1_inputs, axis=0)
        timestep2 = tf.boolean_mask(bilstm, masks_2_inputs, axis=0)
        mlp_inputs = tf.keras.layers.concatenate([timestep1, timestep2], axis=1)
        bilstm_model = tf.keras.Model(inputs=word_model.inputs + [masks_1_inputs, masks_2_inputs], outputs=mlp_inputs)
        # Model
        dense = tf.keras.layers.Dense(mlp_units, input_shape=(lstm_units * 4,), activation='relu')(bilstm_model.output)
        dropout = tf.keras.layers.Dropout(mlp_dropout)(dense)
        probas = tf.keras.layers.Dense(trans_size, activation='softmax')(dropout)
        self._model = tf.keras.Model(inputs=bilstm_model.inputs, outputs=probas)
        self._model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def learn(self, batch_size, patience, epochs, train_y, validation_split, train_tag_ids, train_dep_ids,
              train_char_ids, train_word_vectors, train_masks_1, train_masks_2):
        return self._learn(batch_size, patience, epochs, train_y, validation_split, train_tag_ids, train_dep_ids,
                           train_char_ids, train_word_vectors, train_masks_1, train_masks_2)

    def save(self):
        self._save(self.__filename)

    def load(self):
        self._load(self.__filename)
        return self

    def predict(self, tag_codes, dep_codes, char_codes, word_vectors, masks_1, masks_2):
        batch_probas = self._model.predict(
            [np.array(tag_codes), np.array(dep_codes), np.array(char_codes), np.array(word_vectors), np.array(masks_1),
             np.array(masks_2)])
        return [np.argmax(probas) for probas in batch_probas]
