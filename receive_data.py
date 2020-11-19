from datetime import datetime

import mne
import numpy as np
from pylsl import StreamInlet, resolve_stream

FREQ = 250

EEG_BANDS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 32),
    'gamma': (32, 100)
}

BANDS_EVENTS = {
  'alpha': 'Meditação',
  'beta': 'Concentração'
}

class ProcessEeg:
  def __init__(self, info):
    self.info = info
    self.current_max_band = None


  def get_bandpowers(self, data):
      bandpowers = {}

      for band in EEG_BANDS:
          bp, _ = mne.time_frequency.psd_welch(
              data, n_per_seg=FREQ, fmin=EEG_BANDS[band][0], fmax=EEG_BANDS[band][1])
          bandpowers[band] = np.average(bp)

      return bandpowers


  def sort_bandpowers(self, bandpowers):
      return {k: v for k, v in sorted(bandpowers.items(), key=lambda item: item[1], reverse=True)}


  def get_relative_power(self, sorted_bandpowers):
      iterator = iter(sorted_bandpowers.values())

      max = next(iterator)
      second_max = next(iterator)

      return second_max * 100 / max


  def bandpass_filter(self, raw):
      for i in range(5):
          raw = raw.filter(l_freq=5., h_freq=50.0)

      return raw


  def process_buffer(self, buffer):
      # Faz o transpose para que os canais fiquem como colunas
      sample = np.transpose(buffer)

      # Cria o RawArray com os dados
      raw = mne.io.RawArray(sample, self.info)

      # Aplica o filtro
      raw_filtered = self.bandpass_filter(raw)

      # Extrai as bandpowers dos dados
      bandpowers = self.get_bandpowers(raw_filtered)

      # Ordena pela intensidade
      sorted_bandpowers = self.sort_bandpowers(bandpowers)

      max_band = next(iter(sorted_bandpowers.keys()))

      # Verifica se o evento terminou
      if self.current_max_band != max_band:
        if self.current_max_band is not None:
          print('Sinal {} interrompido ({}).'.format(self.current_max_band, BANDS_EVENTS.get(self.current_max_band, 'DESCONHECIDO')))

        print('Sinal {} detectado ({}).'.format(max_band, BANDS_EVENTS.get(max_band, 'DESCONHECIDO')))

        self.current_max_band = max_band

      # Imprime a banda mais intensa
      print('Sinal mais forte atualmente: {}\t Intensidade relativa: {}'.format(
          max_band,
          self.get_relative_power(sorted_bandpowers)
      ))



def main():
    info = mne.create_info(
      ch_names=['1', '2', '3', '4', '5', '6', '7', '8'], sfreq=FREQ, ch_types='eeg')

    process_eeg = ProcessEeg(info)

    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])

    chunks = []

    while True:
        chunk, _ = inlet.pull_chunk(timeout=1, max_samples=250)

        chunks.append(np.array(chunk))

        if len(chunks) < 5:
            continue

        process_eeg.process_buffer(np.concatenate(chunks))

        chunks = chunks[1:]


if __name__ == "__main__":
    with mne.utils.use_log_level('error'):
        main()
