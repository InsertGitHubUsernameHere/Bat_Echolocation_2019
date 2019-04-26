# Bat_Echolocation

## Introduction
Bat scientists at UNCG record bat calls from all over the state. Doing research on these calls can require years of manual work. Batalog seeks to do that automatically in a web interface, using deep learning techniques to catalog bat calls. The calls are stored in Zero Crossing format. Once the data is cleaned of noise, the bat calls will be clustered according to their shapes, and then classified for future scientific research. If all goes well, we will also be able to predict the nature of the calls based on metadata such as the time, location, and season that the calls were recorded in. The project is written in Python.

<img width="600" alt="bat echolocation" src="https://www.batconservationireland.org/wp-content/uploads/2013/10/EcholocationII.jpg">

## Documents and Presentation

[Progress Report 1](https://github.com/InsertGitHubUsernameHere/Bat_Echolocation_2019/tree/master/doc/2019/Slides/presentation1.pdf)

* [Progress Report 1.5](https://github.com/InsertGitHubUsernameHere/Bat_Echolocation_2019/tree/master/doc/2019/Slides/presentation1.5.pdf)

[Progress Report 2](https://github.com/InsertGitHubUsernameHere/Bat_Echolocation_2019/tree/master/doc/2019/Slides/presentation2.pdf)

* [Progress Report 2.1](https://github.com/InsertGitHubUsernameHere/Bat_Echolocation_2019/tree/master/doc/2019/Slides/presentation2.1.pdf)

* [Progress Report 2.2](https://docs.google.com/presentation/d/1wq229-x5hRvf6A8AKn8MXCq1HauLx43L18w4EComRlw/edit#slide=id.g4f924e4f3e_2_110)

* [Progress Report 2.3](https://github.com/InsertGitHubUsernameHere/Bat_Echolocation_2019/tree/master/doc/2019/Slides/presentation2.3.pdf)

* [Progress Report 2.4](https://docs.google.com/presentation/d/1PnWJF2w1unStshIkm4f0KwYNk9qJu1a3GIUX_r6sfMY/edit?usp=sharing)

* [Progress Report 2.5](https://docs.google.com/presentation/d/1XX0kTizRAIy__HtAYI6UAXHPCf0-MNrwxIiZXW_qWdU/edit?usp=sharing)

* [Progress Report 2.6](https://docs.google.com/presentation/d/1e-beTzMgL5sZSX1uiKZIXkNh6UIbwHyht03F8gaYr0U/edit#slide=id.g4f924e4f3e_2_110)

[Progress Report 3](https://docs.google.com/presentation/d/1bcQKZUBc3wwKHkR5AEyLSz5nDF7gJZVRbPa4vWUJplM/edit#slide=id.g558d802864_1_0)

[Final Progress Report](https://www.canva.com/design/DADYERhZuhQ/share?token=4oMtK1hIZi1BjXPHGj9kLQ&role=EDITOR)

[Batalog Project Document](https://docs.google.com/document/d/1jJgxoAWclTfXR5WuWl7eNxvBmqgRZZZUhYIx0BMW1Hs/edit?usp=sharing)

## Members

Current:

* [Hadi Soufi](https://github.com/HadiSoufi)

* [Thien Le](https://github.com/InsertGitHubUsernameHere)

* [Kevin Keomalaythong](https://github.com/kkeomalaythong)

* [Rahim Jawaid](https://github.com/aRahimIqbal)

* [David Massey](https://github.com/dlmassey)

Former:

* [Yang Peng](https://github.com/yangp18)

* [Bety Rostandy](https://github.com/brostandy)

## Goals

1. [Extraction](https://plot.ly/~souhad/13/zc-noisy-zc-smoothed-zc-noiseless/):
Extract meaningful signal from noise.

2. [Clustering](https://github.com/UNCG-CSE/Bat_Echolocation/blob/master/src/clustering_yang.ipynb):
Categorize the extracted calls into different types using clustering techniques.

3. [Classification](https://github.com/UNCG-CSE/Bat_Echolocation/blob/master/src/clustering_yang.ipynb):
Classify if a Bat Echolocation (zero-crossing files) contains abnormal calls (i.e. social calls, foraging calls).
