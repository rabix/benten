# Benten (pre-alpha) 

This is a workflow helper for [Common Workflow Language](https://www.commonwl.org/) documents.

<img align="right" height="150px" src="media/benten-icon.png"></img>
Many advanced CWL users are comfortable creating tools and workflows "by hand"
using a plain text editor. When creating complex enough workflows navigating 
and editing the resultant document and sub-documents can get tedious. Keeping
track of the bigger picture (what components have been added, what connections
have been set) can also get hard. _Benten_ is a CWL development tool that 
helps with navigating, visualizing and editing workflows. 

_Benten_ is written using Python and [Pyside2] (QT for Python)

[Pyside2]: https://doc.qt.io/qtforpython/

[![Tests](https://travis-ci.com/rabix/benten.svg?branch=master)](https://travis-ci.com/rabix/benten)
[![codecov](https://codecov.io/gh/rabix/benten/branch/master/graph/badge.svg)](https://codecov.io/gh/rabix/benten)


# Installation

Benten requires Python 3.7. (I prefer to set up a Python 3.7 virtual env)
```
python3 --version  # -> Python 3.7.1      (Verify python version)
python3 -m virtualenv ~/.venvs/benten   # Create virtual env - I prefer this
. ~/.venvs/benten/bin/activate          # Activate virtual env
pip3 install git+https://github.com/rabix/benten.git            # Install from github master branch
# pip3 install git+https://github.com/rabix/benten.git@develop  # Install from github develop branch
benten -v <your-workflow-name.cwl>      # Open your-workflow-name.cwl in Benten with debug logging
```

# [Tutorial](docs/tutorial.md)
![2019.03.24](https://lh3.googleusercontent.com/i5mDr9WSKWg9c38XhIpzR6d3BmxvfmKlaWBAheh36A5Wuk7ZaNxDf_vm5nEitWSF0wNQn1937OqqA-BOkmhgDldfp1fm-A_pUKMDIJRAvb1OHDPwQtQRcwpvrroVGsUDFtuFqqzsoSZKz9H7Ra71QM8VTjz1yfBFI1Eqjg_cKN-UxPpjErGxhAEduzvg1Eq61u_B_f_sdmBRG6ZIOyapMZSuQPbrQY6FHShJTfR8meS8WqVC8hE4DS4Zi9fgq5FHSHWT2y4vJFvzy1b06XMwKSvDr1s8TrXseAtDxvvgomaFAxWgJmWPbKANN3V5xp4ILSVVeAjuSkGtBIOogIdF4QRGp2flviXfOPh2nFzUjeZ5btBiXbIYlXSQWJRdR84ROrXh8i-kKsrn5NusRIta8aH0yTv6MTKNfxtWC8GVGaN-l9T-wdOh4Xejyre8shl4R9HatEozKg7M53AgaewpDzUvecnksyMqDNnn3f023_4EE6A93k67VuU_aewOUFoYAqvm7VLYJRmy-pmv5sdkHuwzOHxJpWnqn1-q7zYa7ZbYyk-A9yvmPGRmU3t8GDRXQ-cso6HXWKamasMW8UuhAek6MvP1Y7NTAnLknTG6L7k_yG7kv0NQZ40eZwc43QdUNDmgMpT2Lf94sOZY4KuKrJPtz5XvyQ9tFVRqEkFWE9zeYEojVPIeLCwRgGW_so_Mc3Q6Q5AO-iuj4Z_qvBmZA10P=w800-h464-no)


# License
[Apache 2.0](LICENSE)


# Acknowledgments

**QT**: I've been using QT for C++ projects since 2001. It is awesome to be still 
using this tool-kit two decades later and via Python. Many thanks to the
great [QT](https://www.qt.io/) team, and the [Pyside2](https://wiki.qt.io/Qt_for_Python) 
(QT for Python) team. Pyside2 is distributed under the LGPL.

**QT dark theme**: From https://github.com/ColinDuquesnoy/QDarkStyleSheet

**[ACE editor]**: It's still amazing to me that I can run a javascript app in my
Python desktop app. ACE is distributed under the BSD license.

[Ace editor]: https://ace.c9.io/


# What's in a name? 

**Saraswati** is the Hindu goddess of learning and knowledge and a long time ago 
she visited Japan, where she is known as [Benzaiten] (**Benten** for short) and 
her sitar has morphed into a Japanese _biwa_ but she has kept some of her many arms.

Benzaiten is the goddess of everything that flows: water, time, words, speech, 
eloquence, music and by extension, knowledge. Therefore _Benten_ is an 
appropriate goddess for scientific workflow developers.

[Benzaiten]: https://en.wikipedia.org/wiki/Benzaiten 

_References_
- [Wikipedia page](https://en.wikipedia.org/wiki/Benzaiten)
- [Benzaiten (Benten): Japan’s Goddess of Reason ](http://yabai.com/p/3200) - a much more detailed history

---

<div align="right">
<sub>(c) 2019 Seven Bridges Genomics. Rabix is a registered trademark of Seven Bridges Genomics</sub>
</div>