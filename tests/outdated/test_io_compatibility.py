from io import open
from sys import path
#----------------------------------------------------------
from ndatautils.datapath import DataPath
#----------------------------------------------------------

instrument = "RESEDA"
propnum = 14891
root = "/home/lbeddric/Documents/Data/RESEDAdata"
ending = ".pad"

#-------------------------------------------------------------------------

padpath = DataPath(instrument, propnum, root, ending)

with open(padpath(144052), 'rb') as f:
	data = f.readlines()
	decoded = []
	for ind, dline in enumerate(data):
		try:
			decoded.append(dline.decode("utf-8"))
		except:
			pass
#			print(ind)
print(decoded[-587:-582])
#print(decoded[-5:])
print("Length data list    : ", len(data))
print("Length decoded list : ", len(decoded))
#print(data[41:46])
