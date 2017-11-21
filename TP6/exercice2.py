def read_csv():
    first_line = True
    with open('diabetes1.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        dico = {}
        list_header = None

        for row in spamreader:
            if first_line:
                first_line = False
            else:
                dico[row[11]] = row[]

        return (list_header, dico)

def compute():
