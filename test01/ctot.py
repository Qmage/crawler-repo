import sys,csv
with open('BigSale_products.csv', 'rb') as csvfile:
	with open('BigSale_products.tsv', 'w') as tsvfile:
		for row in csv.reader(csvfile):
			tsvfile.write('\t'.join(row))
			tsvfile.write('\n')
			
