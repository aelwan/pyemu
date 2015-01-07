pyemu
=====

a set of python modules for linear-based computer model uncertainty analyses

What is pyemu?
================

pyemu is a set of python modules for uesr-friendly linear-based computer model uncertainty analysis.  pyemu is closely linked to the open-source suite PEST (Doherty 2010a and 2010b, and Doherty and other, 2010) and PEST++ (Welter and other, 2012), which are tools for model-independent parameter estimation.  Several equations are implemented, including Schur's complement for conditional uncertainty propagation (the foundation of the PREDUNC suite from PEST) and error variance analysis (the foundation of the PREDVAR suite of PEST).

Examples
========

Two example ipython notebooks are used to demostrate the use of Schur's complement for uncertainty and data worth analysis and the use of error variance analysis to help design parameterizations that minimize the predictive bias generated by model error.  Both examples use a synthetic SEAWAT (Langevin and others, 2007)  model with 601 parameters that is based on the Henry  saltwater intrusion problem (Henry, 1964). 

Links
=====

[PEST - http://www.pesthomepage.org/](http://www.pesthomepage.org/)

[PEST++ - http://www.inversemodeler.org/](http://www.inversemodeler.org/)

[https://github.com/dwelter/pestpp](https://github.com/dwelter/pestpp)

References
==========

Doherty, J., 2010a, PEST, Model-independent parameter estimation—User manual (5th ed., with slight additions):
Brisbane, Australia, Watermark Numerical Computing.

Doherty, J., 2010b, Addendum to the PEST manual: Brisbane, Australia, Watermark Numerical Computing.

Doherty, J.E., Hunt, R.J., and Tonkin, M.J., 2010, Approaches to highly parameterized inversion: A guide to using PEST for model-parameter and predictive-uncertainty analysis: U.S. Geological Survey Scientific Investigations Report 2010–5211, 71 p., available at http://pubs.usgs.gov/sir/2010/5211.

Henry, H.R., 1964, Effects of dispersion on salt encroachment in coastal aquifers: U.S. Geological Survey Water-Supply Paper 1613-C, p. C71-C84.

Langevin, C.D., Thorne, D.T., Jr., Dausman, A.M., Sukop, M.C., and Guo, Weixing, 2008, SEAWAT Version 4: A Computer Program for Simulation of Multi-Species Solute and Heat Transport: U.S. Geological Survey Techniques and Methods Book 6, Chapter A22, 39 p.

Welter, D.E., Doherty, J.E., Hunt, R.J., Muffels, C.T., Tonkin, M.J., and Schreüder, W.A., 2012, Approaches in highly parameterized inversion—PEST++, a Parameter ESTimation code optimized for large environmental models: U.S. Geological Survey Techniques and Methods, book 7, section C5, 47 p., available at http://pubs.usgs.gov/tm/tm7c5.



