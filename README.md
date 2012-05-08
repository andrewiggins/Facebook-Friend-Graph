Facebook Friend Graph
=====================

---

Overview
========

The purpose of this package is to generate a [GraphML][2] file
which can be used to make graphs like the ones created by following the 
directions outlined in a [presentation][1] by Sociomantic Labs titled 
*Facebook Network Analysis*.

This software produces a file comparable to the one the **Netvizz** Facebook 
app (referenced in the [presentation][1]) would provide. So if you follow the 
[presentation][1] directions starting with "1. Gephi: Open", replacing 
the `.gdf` file from *Netvizz* with the `.graphml` file this software generates, 
you will get a graph like the one in the [presentation][1].

---

Requirements
============

1. [Python 2.7](http://www.python.org/):

    - The programming language this software is written in. Download it and run 
    this software by executing `python main.py` in a terminal. Or, if you are 
    using Windows, double-click `main.py`.

2. A web browser:

    - A web browser is required for Facebook authentication. Facebook 
    authentication is necessary to access friend's list. No personal information 
    is used or stored anywhere, only your friends list and the mutual friends 
    you and your friend share is accessed and mapped in the GraphML file.

    - This software has been tested using [Google Chrome](http://www.google.com/chrome).

3. [Gephi](http://www.gephi.org) (*optional*)

    - Gephi is the program the [presentation][1] uses to create a graph from the [GraphML][2] 
    file this software creates. Not required to run this software.

---

Usage
=====

`$ python main.py`

No command line arguments are available.

---

Author
======

Andre Wiggins (drewigg@gmail.com)

[1]: http://www.slideshare.net/sociomantic/facebook-network-analysis-using-gephi-3996673 "Facebook Network Analysis Using Gephi"
[2]: http://graphml.graphdrawing.org/ "GraphML"