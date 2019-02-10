import pandas as pd

def predictive_data(filename):

	#If there is not a full seasons worth of data (600 PA), then it will move the
	#players stats towards either average or replacement as a function of the same
	#size
	type = 'replacement' #either average or replacement

	#Assign the stats as declared in the 'type' statement above
	if type == 'average':
		stats = [0.248, 0.318, 0.409, 0.085, 0.223]
	if type == 'replacement':
		stats = [0.200, 0.272, 0.314, 0.042, 0.304]


	input_data = pd.read_csv(filename)
	output_data = pd.DataFrame()

	#Fixes the columns that have % in thim by striping the % and turning it into
	#a decimal (ex. 85% to 0.85)
	input_data['BB%'] = (input_data['BB%'].str.strip('%').astype(float))*0.01
	input_data['K%'] = (input_data['K%'].str.strip('%').astype(float))*0.01
	input_data['Pull%'] = (input_data['Pull%'].str.strip('%').astype(float))*0.01
	input_data['IFH%'] = (input_data['IFH%'].str.strip('%').astype(float))*0.01
	input_data['Soft%'] = (input_data['Soft%'].str.strip('%').astype(float))*0.01
	input_data['BUH%'] = (input_data['BUH%'].str.strip('%').astype(float))*0.01
	input_data['Hard%'] = (input_data['Hard%'].str.strip('%').astype(float))*0.01
	input_data['LD%'] = (input_data['LD%'].str.strip('%').astype(float))*0.01
	input_data['Oppo%'] = (input_data['Oppo%'].str.strip('%').astype(float))*0.01
	input_data['Med%'] = (input_data['Med%'].str.strip('%').astype(float))*0.01
	input_data['HR/FB'] = (input_data['HR/FB'].str.strip('%').astype(float))*0.01


	output_data['Name'] = input_data['Name']

	#Applies the predicitve equations as described in the writeup, then weights
	#them based on the sample size as defined at the top of this function
	output_data['AVG'] = ((input_data['AVG']*0.75 + input_data['Pull%']*-0.37 \
	+ input_data['IFH%']*0.49 + input_data['Soft%']*-0.34 + input_data['BABIP']*-0.47 \
	+ 0.377)*(input_data['PA']/600)) + ((1-input_data['PA']/600)*stats[0])

	output_data['OBP'] = ((input_data['OBP']*0.84 + input_data['Pull%']*-0.25 \
	+ input_data['BUH%']*0.02 + input_data['BABIP']*-0.345 + input_data['IFH%']*0.34 \
	+ 0.269)*(input_data['PA']/600)) + ((1-input_data['PA']/600)*stats[1])

	output_data['SLG'] = ((input_data['wRAA']*0.003 + input_data['BB%']*-0.77 \
	+ input_data['IFH%']*0.79 + input_data['Hard%']*0.44 + input_data['Pull%']*-0.29 \
	+ 0.37)*(input_data['PA']/600)) + ((1-input_data['PA']/600)*stats[2])

	"""
	output_data['BB%'] = ((input_data['BB%']*0.86 + input_data['HR/FB']*0.17 \
	+ input_data['SLG']*-0.10 + input_data['LD%']*-0.13 + input_data['BUH%']*-0.13 \
	+ 0.068)*(input_data['PA']/600)) + ((1-input_data['PA']/600)*stats[3])
	"""

	output_data['BB%'] = output_data['OBP'] - output_data['AVG']

	output_data['K%'] = ((input_data['K%']*0.9 + input_data['Oppo%']*-0.34 \
	+ input_data['BB/K']*0.04 + input_data['PA']*-0.00005 + input_data['Pull%']*-0.14 \
	+ 0.17)*(input_data['PA']/600)) + ((1-input_data['PA']/600)*stats[4])

	return output_data

