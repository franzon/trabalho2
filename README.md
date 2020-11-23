# Reconhecimento de padrões - Trabalho 2

## Objetivo

Identificar os seguintes eventos a partir dos sinais gravados utilizando o OpenBCI:

- Mordida
- Piscar dos olhos
- Ritmos alpha (meditação)
- Ritmos beta (concentração)

## Resultados

Foi possível identificar os ritmos alpha e beta, utilizando o método `psd_welch` do `mne` para calcular as bandas. Foram realizados testes com alguns métodos do pacote `mne`, como o `find_eog_events` para identificar os eventos como a mordida e o piscar dos olhos, porém não obtivemos bons resultados.