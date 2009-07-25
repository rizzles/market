import matplotlib
matplotlib.use('Agg')
from pylab import *

plot ( arange(0,10),[9,4,5,2,3,5,7,12,2,3],'.-',label='sample1' )
plot ( arange(0,10),[12,5,33,2,4,5,3,3,22,10],'o-',label='sample2' )
xlabel('x axis')
ylabel('y axis')
title('GOOG')
savefig("/var/www/test2.png")
