import csv
import math


def read_csv():

    def create_record(header, data):
        record = {}
        for i in range(0, len(header)-1):
            record[header[i]] = data[i]

        return record

    first_line = True
    with open('basket.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        dico = {}
        header = None

        for row in spamreader:
            if first_line:
                header = row
                first_line = False

            else:
                if row[len(row)-1] not in dico:
                    dico[row[len(row)-1]] = []
                    dico[row[len(row)-1]].append((create_record(header, row), 1) )
                else:
                    list_elem = dico[row[len(row)-1]]
                    rec = create_record(header, row)
                    insert = False
                    for record, count in list_elem:
                        if record == rec:
                            list_elem.remove((record, count))
                            list_elem.append((rec, count+1))
                            insert = True
                    if not insert:
                        list_elem.append((rec, 1))

        return dico

def compute(users, observations=None):
    basket = read_csv()

    P_ui = 0.1 # IDEA: it is hardcoded

    def entropy():
        entropy = 0
        for i in range(0, len(users)):
            entropy += P_ui * math.log(P_ui, 2)
        return entropy

    def prouilogpruio(user):
        acc = 0
        for i in range(0, observations):
            # get number of basket according to i for user 'user'
            # multiplier par l'inverse
            list_of_total_basket = basket[user]
            for rec, tot in list_of_total_basket:
                if i == rec:
                    prob = tot/100
                    acc+= prob + log((prob*P_ui/0.01,2))
            acc += basket[user]

    def other_shannon():
        acc = 0
        for i in range(0, len(user)):
            acc += P_ui * prouilogpruio(i)
        return acc

    return entropy + other_shannon

compute(basket.keys(), basket)
