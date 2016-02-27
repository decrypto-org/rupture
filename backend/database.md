target # a particular static target endpoint that the attack can apply to, e.g. gmail, facebook
======
id INT
endpoint TEXT
prefix TEXT
alphabet TEXT

victim # a particular instance of a target for a particular user-victim e.g. dionyziz@gmail.com
======
id INT
target INT
method TEXT # divide & conquer etc.

sampleset # a set of samples collected for a particular victim pertaining to an attack vector used to extend a known secret
=========
id INT
victim INT FOREIGN KEY
amount INT # number of samples contained in set
knownsecret TEXT # known secret before sample set was collected
started DATETIME # date and time at which sample set collection was started
completed DATETIME # when we stopped collecting samples for this sampleset, successfully or not
success BOOLEAN # whether the samples in this sampleset were all collected successfully

attackvectorelement
===================
sampleset INT FOREING KEY
symbol CHAR
