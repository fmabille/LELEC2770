import csv
from sys import maxsize

class Record:

    def __init__(self, lst):
        self.record = lst

    def __eq__(self, o:object):
        if not isinstance(o, Record):
            return False
        else:
            return o.record == self.record

    def __hash__(self):
        #print(hash(tuple(self.record)))
        return hash(tuple(self.record))

def read_csv_without_modif():
    first_line = True
    with open('diabetes1.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if first_line:
                first_line = False
            else:
                yield Record(row)

def read_csv_with_modif():
    first_line = True
    with open('diabetes1.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if first_line:
                first_line = False
            else:
                age = int(row[2])
                lower_age = (age) - (age%25)
                upper_age = (age) + (25 - (age%25))
                age = str(lower_age) + "-" + str(upper_age)

                chol = int(row[0])
                lower_chol = (chol) - (chol%450)
                upper_chol = (chol) + (450 - chol%450)
                chol = str(lower_chol) + "-" + str(upper_chol)

                yield Record([chol, row[1], age, row[3]])


def k_anonymity(lst):
    dic = {}
    for i in lst:
        if i in dic:
            dic[i] += 1
        else:
            dic[i] = 1
    min_value = maxsize
    for value in dic.values():
        if min_value > value:
            min_value = value
    return value

print(k_anonymity(read_csv_with_modif()))


# Distorsion -> quantité de cassage de la base de donnée
# Possibilité de casser la base de donnée mais il faut faire attention à l'utilité. Trade off between utility and privacy
# Car si on privatise bien la db, utilté énorme et l'inverse
# Du coup "juste-milieu"
