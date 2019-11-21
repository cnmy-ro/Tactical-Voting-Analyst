import numpy as np
import pandas as pd
#excel_file = "data.xlsx"
excel_file = "toy_data.xlsx"

preference_matrix = pd.read_excel(excel_file)
true_pref_matrix = preference_matrix

n_candidates = true_pref_matrix.shape[0]
n_voters = true_pref_matrix.shape[1]

scheme = None
################################################################################
'''  Voting Schemes '''
################################################################################

# Plurality Scheme
def getPluralOutcome(pref_matrix):
    candidate_dict = {}
    for c in range(n_candidates):
        candidate_dict[chr(65+c)] = 0
    # Calculate outcome
    for v in range(n_voters):
        candidate_dict[pref_matrix.T[v,0]] += 1

    candidate_dict.pop('nil', None)
    outcome_list = sorted(candidate_dict.items(), key = lambda kv:(kv[1], kv[0]))
    outcome_list.sort(key=lambda val:val[1], reverse=True)
    outcome_list = np.array(outcome_list)[:,0]
    return outcome_list

# Voting for 2 Scheme
def getVotingForTwoOutcome(pref_matrix, bullet_tactic=False, bullet_voter=None):
    candidate_dict = {}
    for c in range(n_candidates):
        candidate_dict[chr(65+c)] = 0
    #Calculate outcome
    if not bullet_tactic:
        for v in range(n_voters):
            candidate_dict[pref_matrix.T[v,0]] += 1
            candidate_dict[pref_matrix.T[v,1]] += 1
    else:
        for v in range(n_voters):
            if v == bullet_voter:
                candidate_dict[pref_matrix.T[v,0]] += 1
            else:
                candidate_dict[pref_matrix.T[v,0]] += 1
                candidate_dict[pref_matrix.T[v,1]] += 1
    
    candidate_dict.pop('nil', None)
    outcome_list = sorted(candidate_dict.items(), key = lambda kv:(kv[1], kv[0]))
    outcome_list.sort(key=lambda val:val[1], reverse=True)
    outcome_list = np.array(outcome_list)[:,0]
    return outcome_list 

# Anti-plurality Scheme
def getAntiPluralOutcome(pref_matrix, bullet_tactic=False, bullet_voter=None):
    candidate_dict = {}
    for c in range(n_candidates):
        candidate_dict[chr(65+c)] = 0
    # Calculate outcome
    if not bullet_tactic:
        for v in range(n_voters):
            for c in range(n_candidates-1):
                candidate_dict[pref_matrix.T[v,c]] += 1
    else:
        for v in range(n_voters):
            if v == bullet_voter: # for the bullet voter
                candidate_dict[pref_matrix.T[v,0]] += 1
            else: # for all other voters
                for c in range(n_candidates-1):
                    candidate_dict[pref_matrix.T[v,c]] += 1

    candidate_dict.pop('nil', None)
    outcome_list = sorted(candidate_dict.items(), key = lambda kv:(kv[1], kv[0]))
    outcome_list.sort(key=lambda val:val[1], reverse=True)
    outcome_list = np.array(outcome_list)[:,0]
    return outcome_list

# Borda Scheme
def getBordaOutcome(pref_matrix, bullet_tactic=False, bullet_voter=None):
    candidate_dict = {}
    for c in range(n_candidates):
        candidate_dict[chr(65+c)] = 0

    # Calculate outcome
    if not bullet_tactic:
        for v in range(n_voters):
            for c in range(n_candidates):
                candidate_dict[pref_matrix.T[v,c]] += n_candidates-1-c
    else:
        for v in range(n_voters):
            if v == bullet_voter:
                candidate_dict[pref_matrix.T[v,0]] += n_candidates-1

            else:
                for c in range(n_candidates):
                    candidate_dict[pref_matrix.T[v,c]] += n_candidates-1-c

    candidate_dict.pop('nil', None)
    #outcome_list = [(k,v) for k,v in candidate_dict.items()]
    outcome_list = sorted(candidate_dict.items(), key = lambda kv:(kv[1], kv[0]))
    outcome_list.sort(key=lambda val:val[1], reverse=True)
    outcome_list = np.array(outcome_list)[:,0]
    return outcome_list

# Outcome Selector
def getOutcome(pref_matrix, bullet_tactic=False, bullet_voter=None):
    global scheme
    if scheme == '1':
      return getPluralOutcome(pref_matrix)
    elif scheme == '2':
        return getVotingForTwoOutcome(pref_matrix, bullet_tactic, bullet_voter)
    elif scheme == '3':
      return getAntiPluralOutcome(pref_matrix, bullet_tactic, bullet_voter)
    elif scheme == '4':
      return getBordaOutcome(pref_matrix, bullet_tactic, bullet_voter)

################################################################################
'''  Happiness calculation '''
################################################################################
def getVoterHappiness(v, outcome, voter_true_pref): # Compare the given Voter's TRUE Preference with the given Outcome
    W = list(range(1, n_candidates+1)) # weights
    W.reverse()

    d_i = 0

    for c in range(n_candidates):
        k = n_candidates - np.argwhere(outcome == voter_true_pref[c])[0][0] # position of the candidate in outcome (indexed form bottom)
        j = n_candidates - c # position of the candidate in the voter's pref (indexed form bottom)
        d_ij = k - j
        d_i += W[c]*d_ij
    voter_happiness = 1/(1+abs(d_i))

    return voter_happiness


# Happiness calculation
def getHappiness(outcome, true_pref_matrix):
    W = list(range(1, n_candidates+1)) # weights
    W.reverse()

    total_happiness = 0
    voter_happiness_list = []
    for v in range(n_voters):
        voter_true_pref = true_pref_matrix[:,v].copy()
        voter_happiness = getVoterHappiness(v, outcome, voter_true_pref)
        total_happiness += voter_happiness
        voter_happiness_list.append(voter_happiness)
    return total_happiness, voter_happiness_list

################################################################################
'''  Tactics  '''
################################################################################
def _comproTactic(v, voter_true_pref, true_pref_matrix): # Given the voter 'v' brute force over all possible compromises. Then choose the best one.
    global scheme
    O = getOutcome(true_pref_matrix)

    # Default values for the best option
    v_h_compro_max =  getVoterHappiness(v, O, voter_true_pref)
    voter_pref_best = voter_true_pref.copy()

    for ci in range(1, n_candidates): # Start from the 2nd preference of the voter. This one will be compromised
        for cj in range(0, n_candidates):
            if cj != ci:
                voter_pref = voter_true_pref.copy()
                # Swap the values
                temp = voter_pref[ci]
                voter_pref[ci] = voter_pref[cj]
                voter_pref[cj] = temp
                # Get voter happiness
                pref_matrix = true_pref_matrix.copy()
                pref_matrix[:,v] = voter_pref.copy()
                O_compro = getOutcome(pref_matrix)
                v_h_compro = getVoterHappiness(v, O_compro, voter_true_pref)

                if v_h_compro > v_h_compro_max: # Updating the best option
                    v_h_compro_max = v_h_compro
                    voter_pref_best = voter_pref.copy()

    modified_pref_matrix = true_pref_matrix.copy()
    modified_pref_matrix[:,v] = voter_pref_best.copy()
    O_compro = getOutcome(modified_pref_matrix)
    return voter_pref_best, O_compro, v_h_compro

def _buryTactic(v, voter_true_pref, true_pref_matrix):
    global scheme
    O = getOutcome(true_pref_matrix)

    # Default values for the best option
    v_h_bury_max =  getVoterHappiness(v, O, voter_true_pref)
    voter_pref_best = voter_true_pref.copy()

    for ci in range(0, n_candidates-1): # Stop at 2nd-last preference of the voter. This one will be buried
        for cj in range(0, n_candidates):
            if cj != ci:
                voter_pref = voter_true_pref.copy()
                # Swap the values
                temp = voter_pref[ci]
                voter_pref[ci] = voter_pref[cj]
                voter_pref[cj] = temp
                # Get voter happiness
                pref_matrix = true_pref_matrix.copy()
                pref_matrix[:,v] = voter_pref.copy()
                O_bury = getOutcome(pref_matrix)
                v_h_bury = getVoterHappiness(v, O_bury, voter_true_pref)

                if v_h_bury > v_h_bury_max: # Updating the best option
                    v_h_bury_max = v_h_bury
                    voter_pref_best = voter_pref.copy()

    modified_pref_matrix = true_pref_matrix.copy()
    modified_pref_matrix[:,v] = voter_pref_best.copy()
    O_bury = getOutcome(modified_pref_matrix)
    return voter_pref_best, O_bury, v_h_bury

def _bulletTactic(v, voter_true_pref, true_pref_matrix):
    global scheme
    voter_pref_bullet = voter_true_pref[0] # Voter votes only for the most preferred candidate
    modified_pref_matrix = true_pref_matrix.copy()
    modified_pref_matrix[0,v] =  voter_pref_bullet
    #modified_pref_matrix[1:,v] = 'nil'
    O_bullet = getOutcome(modified_pref_matrix, bullet_tactic=True, bullet_voter=v)
    v_h_bullet = getVoterHappiness(v, O_bullet, voter_true_pref)

    return voter_pref_bullet, O_bullet, v_h_bullet


def applyBestTactic(v, true_pref_matrix):
    global scheme
    O = getOutcome(true_pref_matrix)

    #Get voter happiness
    voter_true_pref = true_pref_matrix[:,v].copy()
    v_h = getVoterHappiness(v, O, voter_true_pref)

    s_v = None

    # Compromise
    v_pref_compro, O_compro, v_h_compro = _comproTactic(v, voter_true_pref, true_pref_matrix)
    # Bury
    v_pref_bury, O_bury, v_h_bury = _buryTactic(v, voter_true_pref, true_pref_matrix)
    # Bullet
    v_pref_bullet, O_bullet, v_h_bullet = _bulletTactic(v, voter_true_pref, true_pref_matrix)

    tactic = np.argmax([v_h_compro, v_h_bury, v_h_bullet]) # Choose the tactic that results in max happiness of the uv
    if tactic == 0:
        if v_h_compro > v_h:
            s_v = ["Voter's strategic preference: {}".format(list(v_pref_compro)), "Strategic outcome: {}".format(list(O_compro)), "Voter happiness: {:.5f}".format(v_h_compro), "O_compro={} better than O={}, Voter happiness rises from {:.5f} to {:.5f}".format(list(O_compro), list(O), v_h, v_h_compro)]
    elif tactic == 1:
        if v_h_bury > v_h:
            s_v = ["Voter's strategic preference: {}".format(list(v_pref_bury)), "Strategic outcome: {}".format(list(O_bury)), "Voter happiness: {:.5f}".format(v_h_bury), "O_bury={} better than O={}, Voter happiness rises from {:.5f} to {:.5f}".format(list(O_bury), list(O), v_h, v_h_bury)]
    elif tactic == 2:
        if v_h_bullet > v_h:
            s_v = ["Voter's strategic preference: {}".format(list(v_pref_bullet)), "Strategic outcome: {}".format(list(O_bullet)), "Voter happiness: {:.5f}".format(v_h_bullet), "O_bullet={} better than O={}, Voter happiness rises from {:.5f} to {:.5f}".format(list(O_bullet), list(O), v_h, v_h_bullet)]

    return s_v

################################################################################
'''  TVA function '''
################################################################################

def TVA(true_pref_matrix):
    # O -- Non-strategic Outcome (list)
    # H -- Non-strategic Happiness (scalar)
    # S -- STrategic voting options (dict)
    # R -- Risk (scalar)
    global scheme
    scheme = input("Choose the voting scheme (1,2,3 or 4): \n1. Plurality \n2. Vote for two \n3. Anti-plurality, \n4. Borda \n\n>> ")

    true_pref_matrix = true_pref_matrix.values

    O = getOutcome(true_pref_matrix) # Get TRUE OUTCOME
    #print(O)
    H, voter_happiness_list = getHappiness(O, true_pref_matrix) # Get TRUE TOTAL HAPPINESS
    #print(H)

    S={}
    for i in range(n_voters): # If for all voters, if their happiness can increase, they can use tactics
        s_i = applyBestTactic(i, true_pref_matrix)
        if s_i is not None:   # If voter i's happiness increases with any strategy
            S["Voter "+str(i+1)] = s_i

    R = len(S)/n_voters

    print("NON-STRETEGIC OUTCOME: ", O)
    print("\nNON-STRETEGIC HAPPINESS: ", H)
    print("\nSTRATEGIC OPTIONS: ")
    for k,v in S.items():
      print(k, ' ---')
      for i in v:
        print(i)
      print('\n')
    print("RISK: ", R)


################################################################################

TVA(preference_matrix)
