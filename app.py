# Creating Env = virtualenv env 
# Activate env = .\env\Scripts\activate.ps1

from flask import Flask, jsonify
from flask_cors import CORS
import firebase_admin
import random, string
from firebase_admin import credentials
# from firebase_admin import auth
from firebase_admin import firestore
from firebase import firebase
import json

app = Flask(__name__)
CORS(app)
ROOM_CODE = ""

@app.route("/", methods=["GET", "POST"])
def home():
    res = {
        "ROOM CODE" : ROOM_CODE
    }
    return jsonify(res)


# Firebase 
cred = credentials.Certificate('E:/Sanskrut/CRUD/service_account.json')
# cred = credentials.Certificate('/workspace/service_account.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()
firebase = firebase.FirebaseApplication(
    'https://graphic-tensor-328310-default-rtdb.firebaseio.com/', None)


curr_user_uid = ["ENnnA1Hswyf4r8C2PBsHb0maS7u2"]
doc = db.collection('Players').document(curr_user_uid[0]).get()
# contains the information of the current player as dict...
coll = doc.to_dict()
coll_uid = coll["uid"]


@app.route('/create_room', methods=['GET'])
def create_room():
    global ROOM_CODE
    room_code = "".join(random.choice(string.ascii_uppercase +
                        string.ascii_lowercase + string.digits) for _ in range(7))
    print("Room Code : ", room_code)
    ROOM_CODE = room_code
    db.collection("GameRooms").document(room_code).set({
            "state" : "waiting",
            "status" : "not full",
            "player0": {
                    "uid": coll["uid"],
                    "name": coll["name"],
                    "pos" : coll["pos"],
                    "winner" : coll["winner"],
                    "isActive" : coll["isActive"]
                }})
    print("DONE : Room Created ")
    result = {
        "Room Code" : room_code,
        "Room Creation " : "Done"
    }
    # return("Room created") #, 201 ,headers)
    return jsonify(result)



def read(join_code, coll_uid):
    doc = db.collection('GameRooms').document(join_code).get()
    data = doc.to_dict()
    # print(data["player0"]["uid"])
    # print(data["status"])
    status = data["status"]
    for i in range(0, len(data)-2):
        player_uid = data["player"+str(i)]["uid"]
        if coll_uid == player_uid:
            print("Function Exited")
            return True, i, status
    return False, i, status

@app.route('/join_room', methods=['GET'])
def join_room():
    join_code = "sO5xEoO" 
    check_room_db = db.collection('GameRooms').document(join_code).get().exists

    if check_room_db:
        print("Room found in DB")
        check_player_uid, index, room_status = read(join_code, coll_uid)
        print("Index : ", index)

        if room_status == "not full" or check_player_uid:
            if check_player_uid:
                db.collection("GameRooms").document(join_code).update({
                    'player'+str(index): {
                        "uid": coll["uid"],
                        "pos" : coll["pos"],
                        "name" : coll["name"],
                        "winner" : coll["winner"],
                        "isActive" : coll["isActive"]
                    }})
                print("Player Found -> Info Updated")
            else:
                if index <= 2: # it has 3 players Rn
                    db.collection("GameRooms").document(join_code).update({
                        'player'+str(index+1): {
                            "uid": coll["uid"],
                            "pos" : coll["pos"],
                            "name" : coll["name"],
                            "winner" : coll["winner"],
                            "isActive" : coll["isActive"]
                        }})
                    print("Player Not Found -> Info Stored")
                if index == 2:
                    db.collection("GameRooms").document(join_code).update({
                        "status" : "full" 
                    })
                    print("Room Status: FULL")
                else:
                    exit(0)
        else:
            return("Room Status: FULL")
    else:
        return("Invalid Room Code")
        
    return("Room joined")#, 201, headers)



@app.route('/change_game_state', methods=['GET'])
def change_game_state():
    db.collection("GameRooms").document("sO5xEoO").update(
    {
        "state": "running"
    })
    
    print("Room State : Running") #, 201, headers)
    return("Room State : Running") #, 201, headers)



# # -----------------------------------------------------------------
values = []
ladder_values = []

def create_snake_ladder():
    snakeHead = [54, 62, 93, 95, 98]
    snakeTail = [26, 19, 73, 75, 7]
    ladderHead = [14, 45, 84, 67, 91]
    ladderTail = [4, 18, 28, 51, 72]

    for i in range(0, 5):
        values.append(
            {"head": snakeHead[i],
             "tail": snakeTail[i]})
        ladder_values.append(
            {"head": ladderHead[i],
             "tail": ladderTail[i]})
    db.collection("newSnakeLadder").document("snake").set(
        {"values": values})
    db.collection("newSnakeLadder").document("ladder").set(
        {"values": ladder_values})
    # db.collection("newSnakeLadder").document("Winners").set(
    #     {"winnersList": []})    
    # print("Board Creation done")

create_snake_ladder()

# def create_players():
#     names = ["Jatin", "Harshal","Sakshi","Devanshi"]
#     for i in range(0, len(names)):
#         db.collection("NewPlayers").add(
#             {
#                 "name": names[i],
#                 "pos": 0,
#                 "isActive": False,
#                 "winner": False
#             })
#     print("player creation done")
# create_players()


players_id = []
players_fields = []
players = []
    
docs = db.collection('NewPlayers').stream()
for doc in docs:
    idd = doc.id
    players_fields.append(doc.to_dict())
    players_id.append(idd)

for i in range(0, len(players_id)):
    player_dict = {players_id[i]: players_fields[i]}
    players.append(player_dict)

winners = []
intermediate = []

print(players_fields)

def find_player():
    for index in range(len(players)):
        if(players[index][players_id[index]]["isActive"] == True and players[index][players_id[index]]["winner"] == False):
            return players_fields[index], index


def change_player(curr_player, index):
    doc_ref = db.collection("NewPlayers").document(players_id[index]).update({"isActive": False})
    index += 1
    if index == len(players):
        doc_ref = db.collection("NewPlayers").document(players_id[0]).update({"isActive": True})
        player = players_fields[0]
        index = 0
    else:
        doc_ref = db.collection("NewPlayers").document(players_id[index]).update({"isActive": True})
        player = players_fields[index]
    if(player["winner"] == True):
        player = change_player(player, index)
    return player


def move_player(dice_value, curr_player, index):
    new_position = curr_player["pos"] + dice_value
    intermediate.clear()
    intermediate.append(new_position)
    if(new_position > 100):
        return curr_player
    if(new_position == 100):
        print("0000")
        # ------------------------------------
        readWin = db.collection('newSnakeLadder').document("Winners").get()
        coll = readWin.to_dict()

        if(len(coll["winnersList"]) == len(players)-1):
            print("in if statement......................")
            doc_ref = db.collection("newSnakeLadder").document("Winners").update({"winnersList" : firestore.ArrayUnion([players_id[index]])})
            readWin = db.collection('newSnakeLadder').document("Winners").get()
            coll = readWin.to_dict()
            print("Winners List : ", coll["winnersList"])
            exit(0)

        doc_ref = db.collection("NewPlayers").document(players_id[index]).update({"winner": True})
        
        # ------------------------------------
        doc_ref = db.collection("newSnakeLadder").document("Winners").update({"winnersList" : firestore.ArrayUnion([players_id[index]])})
        print("winner added : ", players_id[index])
        # ------------------------------------
        
        doc_ref = db.collection("NewPlayers").document(players_id[index]).update({"isActive": False})
        winners.append(players_fields[index]["name"])
        
    else:
        for i in range(len(values)):
            if(values[i]["head"] == new_position):
                new_position = values[i]["tail"]
                doc_ref = db.collection("NewPlayers").document(players_id[index]).update({"pos": new_position})
                #print(curr_player)
                intermediate.append(new_position)
                break

            elif(ladder_values[i]["tail"] == new_position):
                new_position = ladder_values[i]["head"]
                doc_ref = db.collection("NewPlayers").document(players_id[index]).update({"pos" : new_position})
                #print(curr_player)
                intermediate.append(new_position)
                break
            else:
                continue
    doc_ref = db.collection("NewPlayers").document(
        players_id[index]).update({"pos": new_position})
    return curr_player

@app.route('/roll_dice', methods=['GET'])
def roll_dice():
    dice_value = random.randint(1, 6)
    print(dice_value)
    curr_player, index = find_player()
    print(curr_player)
    if(curr_player["pos"]+dice_value == 100):
        
        curr_player = move_player(dice_value, curr_player, index)

    elif(dice_value == 6):
        if(curr_player["pos"] == 0):
            doc_ref = db.collection("NewPlayers").document(players_id[index]).update({"pos": 1})
            #print(players_id[index])
        else:
            curr_player = move_player(dice_value, curr_player, index)
            if(len(intermediate) == 0):
                final_position = 0
            else:
                final_position = intermediate.pop()
            a = {'dice_value':dice_value, 'intermediate':intermediate,'final_position':final_position, 'winners':winners}
         #'next player':players_fields[index+1]["name"]}
            python2json = json.dumps(a)
        return(python2json)#, 200, headers)

    else:
        if(curr_player["pos"] == 0):
            pass
        else:
            
            curr_player = move_player(dice_value, curr_player, index)

    curr_player = change_player(curr_player, index)
    print(winners)
    if(len(intermediate) == 0):
        final_position = 0
    else:
        final_position = intermediate.pop()
    a = {'dice_value':dice_value, 'intermediate':intermediate,'final_position':final_position, 'winners':winners}
         #'next player':players_fields[index+1]["name"]}
    python2json = json.dumps(a)
    print(python2json)
    return (python2json)#, 201, headers)

# # -----------------------------------------------------------------






if __name__ == "__main__":
    app.run(debug=True, port=5000)
