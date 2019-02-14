# Bat_Echolocation

## Introduction
Bat scientists at UNCG record bat calls from all over the state. Doing research on these calls can require years of manual work. Batalog seeks to do that automatically in a web interface, using deep learning techniques to catalog bat calls. The calls are stored in Zero Crossing format. Once the data is cleaned of noise, the bat calls will be clustered according to their shapes, and then classified for future scientific research. If all goes well, we will also be able to predict the nature of the calls based on metadata such as the time, location, and season that the calls were recorded in. The project is written in Python.

<img width="600" alt="bat echolocation" src="https://www.batconservationireland.org/wp-content/uploads/2013/10/EcholocationII.jpg">

## Documents and Presentation

[Progress Report 1](https://github.com/InsertGitHubUsernameHere/Bat_Echolocation_2019/tree/master/doc/2019/Slides/presentation1.pdf)

[Progress Report 1.5](https://github.com/InsertGitHubUsernameHere/Bat_Echolocation_2019/tree/master/doc/2019/Slides/presentation1.5.pdf)

[Progress Report 2](https://github.com/InsertGitHubUsernameHere/Bat_Echolocation_2019/tree/master/doc/2019/Slides/presentation2.pdf)

[Batalog Project Document](https://docs.google.com/document/d/1jJgxoAWclTfXR5WuWl7eNxvBmqgRZZZUhYIx0BMW1Hs/edit?usp=sharing)

## Members

[Hadi Soufi](https://github.com/HadiSoufi)

[Thien Le](https://github.com/InsertGitHubUsernameHere)

[Kevin Keomalaythong](https://github.com/kkeomalaythong)

[Rahim Jawaid](https://github.com/aRahimIqbal)

[David Massey](https://github.com/dlmassey)

### 2018
[Yang Peng](https://github.com/yangp18)

[Bety Rostandy](https://github.com/brostandy)

## Goals

1. [Extraction](https://plot.ly/~souhad/13/zc-noisy-zc-smoothed-zc-noiseless/):
Extract meaningful signal from noise.

2. [Clustering](https://github.com/UNCG-CSE/Bat_Echolocation/blob/master/src/clustering_yang.ipynb):
Categorize the extracted calls into different types using clustering techniques.

3. [Classification](https://github.com/UNCG-CSE/Bat_Echolocation/blob/master/src/clustering_yang.ipynb):
Classify if a Bat Echolocation(zero-crossing files) contains abnormal calls(i.e. social calls, foraging calls).
