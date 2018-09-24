import sys
sys.path.insert(0, './flask_audio/')

import tensorflow as tf
import keras
import numpy as np
import tempfile
from scipy.io import wavfile
import pyaudio
import wave


from audioset import vggish_embeddings

#expecting a mono, 16000 sampling rate audio file
def labeled_audio(audio_file, save_file):

    avg_window = 10 #size of window for running mean on output
    print_output = True
    sample_length = 3.0
    keras_model = 'flask_audio/models/LSTM_SingleLayer_100Epochs.h5'
    
    RATE = 16000
    CHUNK = int(RATE * sample_length)  # 2 sec chunks
        
    model = keras.models.load_model(keras_model)
    audio_embed = vggish_embeddings.VGGishEmbedder()

    writer = open(save_file, 'w')

    window = [0.5]*avg_window

    wf = wave.open(audio_file, 'rb') #read-only mode

    chunk = wf.readframes(CHUNK)
    
    saved_text = []
    labels = []
    data = []
    
    #read in audio
    chunk_n = 0
    while len(chunk) > 0:
        try:
            arr = np.frombuffer(chunk, dtype=np.int16)
            vol = np.sqrt(np.mean(arr**2))
            embeddings = audio_embed.convert_waveform_to_embedding(arr, RATE)
            p = model.predict(np.expand_dims(embeddings, axis=0))
            window.pop(0)
            window.append(p[0, 0])
            
            #print to console
            print(str(chunk_n*sample_length) + ' - ' + str((chunk_n+1)*sample_length) + ' seconds' + ' - Laugh Score: {0:0.6f} - vol:{1}'.format(p[0, 0], vol))
            
            #write to text that will be returned
            saved_text.append(str(chunk_n*sample_length) + ' - ' + str((chunk_n+1)*sample_length) + ' seconds' + ' - Laugh Score: {0:0.6f} - vol:{1}'.format(p[0, 0], vol))
            
            #write to file
            writer.write(str(chunk_n*sample_length) + ' - ' + str((chunk_n+1)*sample_length) + ' seconds ,{},{}\n'.format(p[0, 0], vol))
            chunk = wf.readframes(CHUNK)
            chunk_n = chunk_n + 1
            
            #save values to return
            labels.append(chunk_n*sample_length)
            data.append(p[0, 0])

        except (KeyboardInterrupt, SystemExit):
            print('Shutting Down -- closing file')
            writer.close()
            
    writer.close()
    return saved_text, labels, data