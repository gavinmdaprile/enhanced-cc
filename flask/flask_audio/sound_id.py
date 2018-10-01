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
    sample_length = 2.0
    keras_model = 'flask_audio/models/LSTM_SingleLayer_100Epochs_Group10.h5'
    
    RATE = 16000
    CHUNK = int(RATE * sample_length)  # 2 sec chunks
        
    model = keras.models.load_model(keras_model)
    audio_embed = vggish_embeddings.VGGishEmbedder()

    writer = open(save_file, 'w')
    writer.write('Seconds,{},{},{},{},{},{}\n'.format('Cheer', 'Laugh', 'Applause','Car','Speech','Siren'))

    window = [0.5]*avg_window

    wf = wave.open(audio_file, 'rb') #read-only mode

    chunk = wf.readframes(CHUNK)
    
    saved_text = []
    
    #read in audio
    chunk_n = 1 #fixing timing
    while len(chunk) > (CHUNK - 1): #changed to quit as soon as fewer than 2 sec left
        try:
            arr = np.frombuffer(chunk, dtype=np.int16)
            embeddings = audio_embed.convert_waveform_to_embedding(arr, RATE)
            p = model.predict(np.expand_dims(embeddings, axis=0))
            window.pop(0)
            window.append(p[0, 0])
            
            #print to console
            print(str(chunk_n*sample_length) + ' - ' + str((chunk_n+1)*sample_length) + ' seconds' + ' {0:0.3f},{1:0.3f},{2:0.3f},{3:0.3f},{4:0.3f},{5:0.3f}'.format(p[0, 0], p[0, 1], p[0, 2], p[0, 3], p[0, 4], p[0, 5]))
            
            #write to text that will be returned
            saved_text.append(str(chunk_n*sample_length) + ' - ' + str((chunk_n+1)*sample_length) + ' seconds, {0:0.3f},{1:0.3f},{2:0.3f},{3:0.3f},{4:0.3f},{5:0.3f}'.format(p[0, 0], p[0, 1], p[0, 2], p[0, 3], p[0, 4], p[0, 5]))
            
            #write to file
            writer.write(str(chunk_n*sample_length) + ' - ' + str((chunk_n+1)*sample_length) + ' seconds, {0:0.3f},{1:0.3f},{2:0.3f},{3:0.3f},{4:0.3f},{5:0.3f}\n'.format(p[0, 0], p[0, 1], p[0, 2], p[0, 3], p[0, 4], p[0, 5]))
            chunk = wf.readframes(CHUNK)
            chunk_n = chunk_n + 1

        except (KeyboardInterrupt, SystemExit):
            print('Shutting Down -- closing file')
            writer.close()
            
    writer.close()