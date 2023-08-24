import random
import statistics as stat


def xor(a, b):
    result = []
    for j in range(1, len(b)):
        if a[j] != b[j]:
            result.append('1')
        else:
            result.append('0')
    return ''.join(result)


# Performs Modulo-2 division
def mod2_division(dividend, divisor):
    # Τελευταίο ψηφίο bit που θα μπει στην πράξη xor
    final_digit_of_slice = len(divisor)  # αργότερα θα χρησιμοποιηθεί ως το bit που "κατεβαίνει"
    # Παίρνω τα πρώτα final_digit_of_slice bits του διαιρετέου
    current_slice = [dividend[j] for j in range(final_digit_of_slice)]
    while final_digit_of_slice < len(dividend):
        next_digit = dividend[final_digit_of_slice]
        if current_slice[0] == '0':
            current_slice = xor('0' * final_digit_of_slice, current_slice) + next_digit
        else:
            current_slice = xor(divisor, current_slice) + next_digit
        # Αυξάνω δείκτη επόμενου bit που θα κατεβάσω
        final_digit_of_slice += 1
    # Τελευταία mod2 αφαίρεση όπου δε θα κατεβούν άλλα bits
    if current_slice[0] == '1':
        current_slice = xor(divisor, current_slice)
    else:
        current_slice = xor('0' * final_digit_of_slice, current_slice)
    return current_slice


def fill_zeroes(message, final_size):  # συμπληρώνει μηδενικά στο message από μπροστά μέχρι να έχει μήκος final_size
    new_num = ['0' for j in range(final_size - len(message))]
    return ''.join(new_num) + message


def alter_sequence(message, prop_of_error):
    list_a = list(message)  # μετατροπή του δυαδικού αριθμού απο string σε λίστα
    flag = False
    for j in range(len(message)):
        rand_num = random.random()
        # Η πιθανότητα ο τυχαίος αριθμός στο [0,1] να είναι μικρότερος από το BER είναι ίση με το BER
        if rand_num <= prop_of_error:
            flag = True
            if list_a[j] == '0':
                list_a[j] = '1'
            else:
                list_a[j] = '0'
    return ''.join(list_a), flag
    # επιστροφή string με το αντίστοιχο αλλαγμένο ή όχι δυαδικό μήνυμα και true αν άλλαξε, false διαφορετικά


def generate_binary_num(num_of_messages, original_message_size):
    my_list = ["0", "1"]
    my_numbers = []
    for j in range(num_of_messages):
        str_form = ''.join(random.choices(my_list, weights=[1, 1], k=original_message_size))
        # παράγεται string μήκος k και ισοπίθανη εμφάνιση των 0 και 1 σε κάθε θέση
        my_numbers.append(str_form)
    return my_numbers  # επιστρέφεται λίστα size τυχαίων δυαδικών αριθμών


def calculate_FCS(message, P, n):
    k = len(message)
    new_zeroes = ['0' for j in range(n-k)]
    filled_message = message + ''.join(new_zeroes)  # n-k μηδενικά στα δεξιά του D
    F = mod2_division(filled_message, P)
    F = fill_zeroes(F, n-k)
    return F


def message_is_altered(message, P):
    remainder = mod2_division(message, P)
    check = remainder.find('1')  # Αν υπάρχει 1 στο υπόλοιπο τότε σίγουρα δεν είναι μηδέν
    if check == -1:  # Αν δε βρεθεί '1' επιστρέφεται -1, δηλαδή αν το υπόλοιπο είναι μηδέν
        return False
    else:
        return True


sample_size = 10000
# Με το συγκεκριμένο μέγεθος δείγματος το πρόγραμμα τερμάτισε σε 1-2 λεπτά
# Παράγω 1.000.000 τυχαία μηνύματα (ισοπίθανη εμφάνιση 0 ή 1) μήκους messages_length
messages_length = int(input("Give the number of digits in the randomly generated messages: "))  # --> k
P_num = input("Give P: ")  # --> len --> n-k-1
T_len = len(P_num) + messages_length + 1  # --> n = len(P) + k + 1
BER = float(input("Give BER: "))

messages = generate_binary_num(sample_size, messages_length)

for i in range(sample_size):
    fcs = calculate_FCS(messages[i], P_num, T_len)
    messages[i] = messages[i] + fcs  # αποθηκεύω το fcs μαζί με το μήνυμα στην ίδια θέση του πίνακα

# Αλλοίωση μηνυμάτων με π.χ. BER = 10^3 (1 στα 1000 bits αλλάζουν) κατά τη μετάδοση
for i in range(sample_size):
    new_message, altered = alter_sequence(messages[i], BER)
    messages[i] = (new_message, altered)


# Υπολογισμός μηνυμάτων που αλλοιώθηκαν και εντοπίστηκαν

# Μηνύματα που ανιχνεύτηκαν από τον CRC ότι έχουν λάθος και όντως έχουν
caught_errors = 0
# Μηνύματα που ανιχνεύτηκαν από τον CRC ότι έχουν αλλοιωθεί αλλά
# δεν έχουν (πρέπει να είναι 0 αν δουλεύει σωστά το πρόγραμμα)
bamboozled_errors = 0
# Συνολικός αριθμός μηνυμάτων που αλλοιώθηκαν
true_errors = 0
for i in range(sample_size):
    if messages[i][1]:
        true_errors += 1
    if message_is_altered(messages[i][0], P_num):  # true αν ο CRC ανιχνεύσει σφάλμα
        if messages[i][1]:  # Το μήνυμα είναι όντως αλλοιωμένο
            caught_errors += 1
        else:
            bamboozled_errors += 1

# print(bamboozled_errors)
print("Sample size: ", sample_size, "messages")
print("There was a total of ", true_errors, "(", true_errors*100/sample_size, "% of messages)", " altered messages")
print("CRC detected ", caught_errors, "(", caught_errors*100/true_errors, "% of all the errors)")
print("Altered messages that were not detected: ", true_errors-caught_errors, "(", (true_errors-caught_errors)*100/true_errors, "% of all errors)")

# Suggested input
#
# 20
# 110101
# 0.001
