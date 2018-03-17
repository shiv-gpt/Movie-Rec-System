import pandas as pd
import scipy
import numpy as np

data_dir = 'G:/major/projectCode/data/movielens/microblog/app/static/db/u1.base'

## Declare a 2-D matrix of size 944*1683 initialized to 0
## This is 1-indexed
user_item_rating_matrix = np.zeros((944, 1683))
##Declare list of genres
genres = ('unknown','Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western');
genreLength = len(genres)

##Lists for movies################
movie_name = []
release_date = []
movie_url = []
movie_genre = []
genreRatingSum = np.zeros((1,20))
genreMovieCount = np.zeros((1,20))
genreAvgRatings = np.zeros((1,20), dtype=float)
avg_rating_user = [0]*944
avg_rating_item = [0]*1683
###################################

#######################
## Declare lists for calculating SUR,SIR and SUIR
sur = []
cos_sur = {}
sir = []
cos_sir = {}
user_item_rating_matrix = np.zeros((944, 1683))
# suir = [[0 for x in range(1683)] for x in range(944)]
#######################
##Create object for the file

def initMatrix():
    data = pd.read_csv(data_dir + 'u1.base', sep='\s+', header=None)
    data.columns = ["user_id", "item_id", "rating", "timestamp"]
    for i in range(0, len(data.user_id)):
            user_id = data.user_id[i]
            item_id = data.item_id[i]
            rating = data.rating[i]
            timestamp = data.timestamp[i]
            user_item_rating_matrix[user_id][item_id] = rating
            ##print "user_id : " + str(user_id) + " item_id : " + str(item_id) + " rating : " + str(rating) + "\n"



def printMatrix(mat, numRows, numCols):
    for i in range(numRows):
        for j in range(numCols):
            print '{:4}'.format(mat[i][j]),

def calcGenre():
    with open(data_dir + 'u.item', 'r') as f:
        s = f.readline().split('|')
        i = 0
        while s != ['']:
            movie_name.append(s[1])
            release_date.append(s[2])
            movie_url.append(s[4])
            g = 0
            for i in range(19):
                if int(s[i+5]) == 1:
                    g += (1<<i)
            movie_genre.append(g)
            s = f.readline().split('|')
            #print s
    return movie_name

##printMatrix(user_item_rating_matrix,8,8)

def cosine_sim(v,u):
    Sum = 0
    su = 0
    sv = 0
    Sum = np.sum(np.multiply(v[0:u.shape[0]],u))
    su = np.sum(np.multiply(u,u))
    sv = np.sum(np.multiply(v,v))
    a = (scipy.sqrt(su)*scipy.sqrt(sv))
    if a > 0:
        return (Sum/a)
    else:
        return 0

def calc_sur(new_user_id,n):
    import Queue as q
    Q = q.PriorityQueue()
    for user_id in range(1,944):
        if(user_id != new_user_id):
            a = cosine_sim(user_item_rating_matrix[user_id],user_item_rating_matrix[new_user_id])
            Q.put((-a,user_id))
    for i in range(n):
        if not Q.empty():
            (a,b) = Q.get()
            sur.append(b)
            cos_sur[b] = -a




def calc_sir(user_id,item_id,n):
    import Queue as Q
    q = Q.PriorityQueue()
    rating_item = np.zeros((1683, 1))
    for i in range(944):
        rating_item[i] = user_item_rating_matrix[i][item_id]
    for i in range(1,1683):
        if(user_item_rating_matrix[user_id][i] != 0 and i != item_id):
            temp = np.zeros((944, 1))
            for j in range(1,944):
                temp[j] = user_item_rating_matrix[j][i]
            val=cosine_sim(rating_item,temp)
            q.put((-val,i))
    for i in range(n):
        if not q.empty():
            (a,b) = q.get()
            sir.append(b)
            cos_sir[b] = -a


def calc_suir(new_user_id,new_item_id):
    for i in range(len(sur)):
        for j in range(len(sir)):
            user_id = sur[i]
            item_id = sir[j]
            if user_id != new_user_id and item_id != new_item_id:
                suir[user_id][item_id] = 1

### Calculate average ratings for each user and each item######################################
def calc_avg_rating_user():
    for user_id in range(1,944):
        S = 0
        C = 0
        for item_id in range(1,1683):
            if(user_item_rating_matrix[user_id][item_id] != 0):
                S += user_item_rating_matrix[user_id][item_id]
                C += 1
        if C > 0:
            avg_rating_user[user_id] = (S*1.0)/C


def calc_avg_rating_item():
    for item_id in range(1,1683):
        S = 0
        C = 0
        for user_id in range(1,944):
            if(user_item_rating_matrix[user_id][item_id] != 0):
                S += user_item_rating_matrix[user_id][item_id]
                C += 1
        if C > 0:
            avg_rating_item[item_id] = (S*1.0)/C

calc_avg_rating_user()
calc_avg_rating_item()

#print avg_rating_user
#print avg_rating_item
##############################################################################################

def euclidean_dist(a,b):
    if a == 0:
        return b
    if b == 0:
        return a
    x = 1.0/(a*a)
    y = 1.0/(b*b)
    return 1.0/(scipy.sqrt(x+y))


## Calculate expected rating value of user k for item m #########################################

def calc_expected_rating(k, m, max_rating_value,avgk,avgm,Lambda,delta):
    expectedRating = 0
    for r in range(1,max_rating_value+1):
        p_with_sur = 0
        numerator = 0
        denominator = 0
        for i in range(len(sur)):
            user_id = sur[i]
            for item_id in range(1,1683):
                pkm = user_item_rating_matrix[user_id][item_id]
                temp1 = avg_rating_user[user_id] - avgk
                temp2 = avg_rating_item[item_id] - avgm
                pkm -= temp1
                pkm -= temp2
                pkm = int(pkm) + 1
                if pkm == r:
                    numerator += cos_sur[user_id]
                denominator += cos_sur[user_id]
        if denominator > 0:
            p_with_sur = (numerator*1.0)/denominator
        numerator = 0
        denominator = 0
        p_with_sir = 0
        for i in range(len(sir)):
            item_id = sir[i]
            for user_id in range(1,944):
                pkm = user_item_rating_matrix[user_id][item_id]
                temp1 = avg_rating_user[user_id] - avgk
                temp2 = avg_rating_item[item_id] - avgm
                pkm -= temp1
                pkm -= temp2
                pkm = int(pkm) + 1
                if pkm == r:
                    numerator += cos_sir[item_id]
                denominator += cos_sir[item_id]
        if denominator > 0:
            p_with_sir = (numerator*1.0)/denominator
        numerator = 0
        denominator = 0
        p_with_suir = 0
        for i in range(len(sur)):
            user_id = sur[i]
            for j in range(len(sir)):
                item_id = sir[j]
                pkm = user_item_rating_matrix[user_id][item_id]
                temp1 = avg_rating_user[user_id] - avgk
                temp2 = avg_rating_item[item_id] - avgm
                pkm -= temp1
                pkm -= temp2
                pkm = int(pkm) + 1
                ed = euclidean_dist(cos_sur[user_id],cos_sir[item_id])
                if pkm == r:
                    numerator += ed
                denominator += ed
        if denominator > 0:
            p_with_suir = (numerator*1.0)/denominator
        #print "sur : " + str(p_with_sur) + "sir : " + str(p_with_sir) + "suir : " + str(p_with_suir)
        p_with_sur *= Lambda*(1-delta)
        p_with_sir *= (1 - Lambda)*(1-delta)
        p_with_suir *= delta
        expectedRating += r*(p_with_sur + p_with_sir + p_with_suir)
    return expectedRating

#########################################################################

   ##########Main Recommender Function############

def recommender(user_id,Lambda,delta,n):
    # initMatrix()
    # calcGenre()
    # user_id = int(raw_input('Enter the user id to continue : '))
    # Lambda = float(raw_input('Enter the value of the parameter Lambda : '))
    # delta = float(raw_input('Enter the value of the parameter delta : '))
    # n = int(raw_input('Enter the number of recommendations : '))
    #f = open('G:/major/projectCode/data/movielens/microblog/app/static/db/f.txt','w')


    import Queue as Q
    predic_rating = Q.PriorityQueue()
    calc_sur(user_id,n)
    #print "sur : "
    #print sur
    C = 0
    MAE = 0
    num = 0
    for item_id in range(0,1683,20):
        C += 1
        if C % 10 == 0:
            print "Calculating for item id : " + str(item_id)
            #f.write("Calculating for item id : " + str(item_id))
        if user_item_rating_matrix[user_id][item_id] == 0:
            sir[:] = []
            cos_sir.clear()
            calc_sir(user_id,item_id,n)
            #print "sir : "
            #print sir
            temp = calc_expected_rating(user_id,item_id,5,avg_rating_user[user_id],avg_rating_item[item_id],Lambda,delta)
            predic_rating.put((-temp,item_id))
            #print "Rating for item " + str(item_id) + " : " + str(temp)
        else:
            sir[:] = []
            cos_sir.clear()
            calc_sir(user_id,item_id,n)
            temp = calc_expected_rating(user_id,item_id,5,avg_rating_user[user_id],avg_rating_item[item_id],Lambda,delta)
            MAE += abs(user_item_rating_matrix[user_id][item_id] - temp)
            num += 1
            #print "actual rating : " + str(user_item_rating_matrix[user_id][item_id]) + " expected rating : " + str(temp)
            #f.write("actual rating : " + str(user_item_rating_matrix[user_id][item_id]) + " expected rating : " + str(temp))
    print "Your recommendations are : " + "\n"
    for i in range(n):
        if not predic_rating.empty():
            (a,b) = predic_rating.get()
            print str(movie_name[b]) + "   " + str(-a)
    print "Mean absolute error : " + str(MAE/num) + " " + str(MAE/1683)
    return predic_rating

# recommender(1, 0.9, 0.9, 10)
