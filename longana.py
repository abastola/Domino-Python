#---------------------------------------------------------------------------------------------------------------------
'''
Name: Arjun Bastola
Class: OPL
Language: Python
Date: 16 December 2017
'''
#---------------------------------------------------------------------------------------------------------------------

import re # regex
import os.path
import json
from random import shuffle

#---------------------------------------------------------------------------------------------------------------------
'''
Function:   Main
Purpose:    Ask user the game inputs or load file and run the tournament.
Parameters: None
Local Variables: tournamentScore - Tournament Score; roundNumber - Round Number; 
				  humanPlayer - Number of Human Player; computerPlayer - number of computer player; 
				  hands - hand of a player; layouts - layout of each player; stocks - stock of the round; 
				  types - type of player (computer/human); totalPlayer - total number of player; 
				  scores - score of players; turn - player with turn; gameType - type of game (new/load)
'''
#---------------------------------------------------------------------------------------------------------------------

def main():
	print("-"*75)
	print(" "*33, "Welcome", " "*33)
	print("-"*75)

	
	tournamentScore = -1
	roundNumber = 0
	humanPlayer = -1
	computerPlayer = 4
	hands = []
	layouts = []
	stocks = []
	types = []
	totalPlayer = 0
	scores = []
	turn = -1
	gameType = ""

	# Ask if user wants to load a file
	while True:
		gameType = input("Do you want to load a game? (y/n) ").upper()
		if gameType in ["Y", "N"]:
			break

	# In case of new game, ask for Tournament Score
	if gameType == "N":
		while True:
			try:
				tournamentScore = int(input("Enter tournament score: "))
			except ValueError:
				print("Invalid Input. Enter a number > 0")
			if tournamentScore > 0:
				break
			else:
				print("Tournament Score must be > 0.")
		while True:
			try:
				humanPlayer = int(input("Enter number of human players: "))
			except ValueError:
				print("Invalid Input. Enter a number > 0")
			if humanPlayer > 0 and humanPlayer < 4:
				break
			else:
				print("Player must be > 0 and less than 4.")

		while True:
			try:
				computerPlayer = int(input("Enter number of computer players: "))
			except ValueError:
				print("Invalid Input. Enter a number > 0")
			if computerPlayer > 0 and computerPlayer < 4 and (computerPlayer+humanPlayer) <5:
				break
			else:
				print("Player must be > 0 and < 4; Also total number of players must be less than or equal to 4.")
		totalPlayer = humanPlayer + computerPlayer
		for n in range(0, totalPlayer ):
			scores.append(0)

	else:
		while True:
			fileName = input("Enter the filname you want to load: ")
			if os.path.exists(fileName):
				data = json.load(open(fileName))
				stocks = [tuple(l) for l in data["Stock"]]
				scores = data["Score"]
				types = data["Type"]
				roundNumber = data["Round"]
				tournamentScore = data["TS"]
				turn = data["Turn"]
				for x in data["Layout"]:
					layouts.append([tuple(l) for l in x])
				for x in data["Hand"]:
					hands.append([tuple(l) for l in x])
				totalPlayer = len(hands)
				break
			else:
				print("File doesn't exist.")

	maximumRound = 7 if totalPlayer <= 2 else 9

	while True:
		# Begin the round
		round = Round(tournamentScore, roundNumber, turn, humanPlayer, computerPlayer, totalPlayer, scores, hands, layouts, stocks, types)

		round.printRoundDetails()

		if len(hands) ==  0 or len(layouts[0]) == 0:
			# Print who placed the round
			print("Player", round.findAndPlaceEngine(), "placed the engine.")

		round.printRoundDetails()
		input("Press enter to continue")
		# Start the round
		scores = round.beginRound()

		round.printRoundDetails()

		if max(scores) > tournamentScore:
			break

		temp = roundNumber
		roundNumber = temp + 1 if roundNumber < maximumRound else 0

		hands = []
		stocks = []

	# Tournament Ends
	player = 0
	print("\nTournament has ended. Players and their scores are: \n")
	print("Player        \t", "Score\n---------------------------")
	for score in scores:
		print("Player", player, "\t", score)
		player += 1

	winnerIndex = scores.index(max(scores))
	print("\nPlayer", winnerIndex, "wins the tournament with", max(scores), "points.")
	exit()

#---------------------------------------------------------------------------------------------------------------------
'''
Class:      Stock
Date:       16 December 2017
Purpose:    Store the stock of each round
			Distribute hand to players
			Draw domino for players
'''
#---------------------------------------------------------------------------------------------------------------------


class Stock:

	def __init__(self, numberOfPlayers, stocks):
		self.stock = []
		if len(stocks):
			self.stock = stocks
		else:
			dominoType = 0
			dominoType = 7 if numberOfPlayers == 2 else 10
			self.stock = [(x, y) for x in range(0, dominoType) for y in range(x, dominoType)]
			shuffle(self.stock)

	def distributeHand(self):
		hand = self.stock[:6]
		self.stock = self.stock[6:len(self.stock)]
		return hand

	def drawDomino(self):
		dominoDrawn = self.stock[0]
		del self.stock[0]
		return dominoDrawn

	def getStock(self):
		return self.stock[:]

#---------------------------------------------------------------------------------------------------------------------
'''
Class:      Hand
Date:       16 December 2017
Purpose:    Store the hand of each player
			Find domino with particular side
			Check for engine
			Delete domino
			Add domino
'''
#---------------------------------------------------------------------------------------------------------------------
class Hand:
	def __init__(self, hand):
		self.hand = hand

	def findDominosWithSide(self, side):
		return [(x, y) for (x,y) in self.hand if x==side or y==side]

	def hasEngine(self, engine):
		return (engine, engine) in self.hand

	def deleteDomino(self, domino):
		self.hand.remove(domino)

	def addDomino(self, domino):
		self.hand.append(domino)

	def getHand(self):
		return self.hand[:]

#---------------------------------------------------------------------------------------------------------------------
'''
Class:      Layout
Date:       16 December 2017
Purpose:    Store the layout of each player
			Get End Pip of each player
			Add domino
'''
#---------------------------------------------------------------------------------------------------------------------
class Layout:
	def __init__(self, layout, type):
		self.layout = layout
		self.type = type

	def getEndPip(self):
		pip1, pip2 = self.layout[len(self.layout)-1]
		return pip2

	def addDomino(self, domino):
		self.layout.append(domino)

	def getLayout(self):
		return self.layout[:]

#---------------------------------------------------------------------------------------------------------------------
'''
Class:      Player
Date:       16 December 2017
Purpose:    Store information of each player
			Print player details after each play
'''
#---------------------------------------------------------------------------------------------------------------------
class Player:
	def __init__(self, id, hand, layout, score, passed, drawn):
		self.id = id
		self.hand = Hand(hand)
		self.layout = Layout(layout, id)
		self.score = score
		self.drawn = False
		self.type = "Computer"

	def printPlayerDetails(self):
		print("Player ID:     " + str(self.id))
		print("Player Type    " + self.type)
		print("Player Score:  " + str(self.score))
		print("Player Hand:   " + str(self.hand.getHand()))
		print("Player Layout:", str(self.layout.getLayout()), "P"+str(self.id))

#---------------------------------------------------------------------------------------------------------------------
'''
Class:      Round
Date:       16 December 2017
Purpose:    Store information of all players and play turn accordidly
			Check if round has ended and declare winner and restart/end round accordigly.
'''
#---------------------------------------------------------------------------------------------------------------------

class Round:

#---------------------------------------------------------------------------------------------------------------------
'''
Function:   __init__
Purpose:    Constructor for a round; Initliaze the round member objects.
Parameters: ts - Tournament Score; roundNumber - Round Number; 
			humanPlayer - Number of Human Player; computerPlayer - number of computer player; 
			hands - hand of a player; layouts - layout of each player; stocks - stock of the round; 
			types - type of player (computer/human); totalPlayer - total number of player; 
			scores - score of players; turn - player with turn; gameType - type of game (new/load)
'''
#---------------------------------------------------------------------------------------------------------------------

	def __init__(self, ts, roundNumber, turn, numberOfHumans, numberOfComputer, totalPlayers, scores, hands, layouts, stocks, types):
		numberOfPlayers = numberOfHumans + numberOfComputer
		self.ts = ts
		self.roundNumber = roundNumber
		self.numberOfPlayers = numberOfHumans + numberOfComputer
		self.stock = Stock(numberOfPlayers, stocks)
		self.players = []
		self.dominoType = 6 if numberOfPlayers == 2 else 9
		self.passed = []
		self.turn = 0
		self.emptyStockDrawCount = 0

		if len(hands):
			for n in range (0, totalPlayers):
				player = Player(n, hands[n], layouts[n], scores[n], False, False)
				player.type = types[n]
				self.passed.append(False)
				self.players.append(player)
				self.turn = turn
				self.numberOfPlayers = totalPlayers
		elif len(layouts):
			for n in range(0, totalPlayers):
				print("HERE")
				hand = Hand(self.stock.distributeHand())
				player = Player(n, hand.getHand(), [], scores[n], False, False)
				self.passed.append(False)
				player.type = types[n]
				self.players.append(player)
				self.numberOfPlayers = totalPlayers
		else:
			for n in range(0, numberOfPlayers):
				hand = Hand(self.stock.distributeHand())
				player = Player(n, hand.getHand(), [], 0, False, False)
				player.score = scores[n]
				self.players.append(player)
				self.passed.append(False)
				if n < numberOfHumans:
					player.type = "Human"
				else:
					player.type = "Computer"

#---------------------------------------------------------------------------------------------------------------------
'''
Function:   printRoundDetails
Purpose:    Print each player's details
Parameters: None
Local Variables: player - loop variable for each player of the round
'''
#---------------------------------------------------------------------------------------------------------------------

	def printRoundDetails(self):
		print("Round:", self.roundNumber+1, "\n"+"Stock:", self.stock.getStock(), "\n"+"-"*75)
		for player in self.players:
			player.printPlayerDetails()
			print("Passed:", self.passed[player.id])
			print('\n')

#---------------------------------------------------------------------------------------------------------------------
'''
Function:  findAndPlaceEngine
Purpose:    Finds engine from a player's hand and places it
Parameters: None
Local Variables: engine - engine of the round, engineFound - to keep track of engine;
				 playerWithEngine - id of player with engine
'''
#---------------------------------------------------------------------------------------------------------------------

	def findAndPlaceEngine(self):
		engine = self.dominoType - self.roundNumber
		engineFound = False
		playerWithEngine = -1
		print("Engine:", engine, engine)
		self.printRoundDetails()
		print("Stock: ", self.stock.getStock())
		input("Press enter to continue...")
		while (not engineFound):
			for player in self.players:
				if player.hand.hasEngine(engine):
					player.hand.deleteDomino((engine, engine))
					engineFound = True
					playerWithEngine = player.id
					break
			for player in self.players:
				if engineFound:
					player.layout.addDomino((engine, engine))
				else:
					if len(self.stock.getStock()):
						player.hand.addDomino(self.stock.drawDomino())
			self.printRoundDetails()

		self.turn = playerWithEngine

		# Change the turn
		turn = self.turn+1
		self.turn = turn if turn < self.numberOfPlayers else 0

		return playerWithEngine

#---------------------------------------------------------------------------------------------------------------------
'''
Function:  beginRound
Purpose:    Find player with turn and play turn
Parameters: None
Local Variables: returnCode - to keep track of how round ended
'''
#---------------------------------------------------------------------------------------------------------------------
	def beginRound(self):
		while True:
			# Print board after player's move
			self.printRoundDetails()

			# Play Turn based on type of player
			if self.players[self.turn].type == "Computer":
				self.playComputerTurn()
			else:
				self.playHumanTurn()

			#check if round has ended
			returnCode = self.checkRoundEnd()

			if returnCode == 1:
				scores = []
				for player in self.players:
					scores.append(player.score)
				return scores

#---------------------------------------------------------------------------------------------------------------------
'''
Function:  findPossibleMoves
Purpose:    Find player's possible moves
Parameters: turn - player object
Local Variables: hand - hand of player, endPip - end point of player's layout
'''
#---------------------------------------------------------------------------------------------------------------------

	def findPossibleMoves(self, turn):
		hand = turn.hand.getHand()
		id = turn.id
		endPip = turn.layout.getEndPip()

		possibleMoves = [(id, (x,y)) for (x,y) in hand if x == endPip or y == endPip]
		for player in self.players:
			if id != player.id:
				endPip = player.layout.getEndPip()
				moves = []
				if self.passed[player.id]:
					moves = [(player.id, (x, y)) for (x,y) in hand if x == endPip or y == endPip]
				else:
					moves = [(player.id, (x, y)) for (x,y) in hand if x == endPip and y == endPip]
				possibleMoves = possibleMoves + moves
		return possibleMoves

#---------------------------------------------------------------------------------------------------------------------
'''
Function:  findBestMove
Purpose:    Find player's best moves
Parameters: moves - possible moves
Local Variables: id - id of side, pip2/pip1 - sides
'''
#---------------------------------------------------------------------------------------------------------------------

	def findBestMove(self, moves):
		if not moves:
			return []
		else:
			maxSum = 0
			bestMove = []
			for move in moves:
				id, domino = move
				pip1, pip2 = domino
				if (pip1 + pip2) > maxSum:
					bestMove = move
					maxSum = pip1+pip2
			return bestMove


#---------------------------------------------------------------------------------------------------------------------
'''
Function:  playComputerTurn
Purpose:    Find computer player's best move and plays it. Draw or pass if necessary.
Parameters: none
Local Variables: currentPlayer - player with turn, possibleMoves - possible move of players, bestMove - best move of player
'''
#---------------------------------------------------------------------------------------------------------------------


	def playComputerTurn(self):

		# Find player's move
		currentPlayer = self.players[self.turn]
		possibleMoves = self.findPossibleMoves(currentPlayer)
		bestMove = self.findBestMove(possibleMoves)

		print("----------------------------------------------------------------------------------\n ")
		print("Turn ID:", currentPlayer.id)
		print("Possible Moves:", possibleMoves)
		print("Best Move:", bestMove)
		print("Stock:", self.stock.getStock() , "\n")

		# Play the move if is not empty
		if bestMove != []:
			id, domino = bestMove
			pip1, pip2 = domino
			endPip = self.players[id].layout.getEndPip()

			# Add tile to appropriate side
			if(pip1 == endPip):
				self.players[id].layout.addDomino((pip1, pip2))
			else:
				self.players[id].layout.addDomino((pip2, pip1))

			print("Player", self.turn, "placed", pip1, pip2, "on side", ("P"+str(id)), "beacause this moves yields the highest sum out of all possible moves.")
			# Delete tile from hand
			currentPlayer.hand.deleteDomino((pip1, pip2))

			# Reset the passed
			for player in self.players:
				self.passed[player.id] = False

			# Reset the empty stock count
			self.emptyStockDrawCount = 0

			# Change the turn
			turn = self.turn+1
			self.turn = turn if turn < self.numberOfPlayers else 0

			currentPlayer.drawn = False

		# Pass or draw a tile
		else:

			#try to draw a tile
			self.drawOrPass(currentPlayer)

		print("----------------------------------------------------------------------------------\n ")

#---------------------------------------------------------------------------------------------------------------------
'''
Function:  drawOrPass
Purpose:    If draw or pass condition, find which and perform.
Parameters: player - player with turn
Local Variables: turn - player with new turn
'''
#---------------------------------------------------------------------------------------------------------------------

	def drawOrPass(self, player):
		if player.drawn:

			# Pass the turn
			self.passed[self.turn] = True
			print("Player", player.id, "passed as the player can't draw twice.")

			# Change the turn
			turn = self.turn+1
			self.turn = turn if turn < self.numberOfPlayers else 0

			# Reset the drawn
			player.drawn = False

		else:
			if len(self.stock.getStock()):

				# Draw a domino
				player.hand.addDomino(self.stock.drawDomino())
				player.drawn = True
				print("Player", player.id, "drew a domino from stock.")

			else:

				# Pass when stock is empty
				self.emptyStockDrawCount += 1
				self.passed[self.turn] = True
				print("Player", player.id, "passed as stock is empty.")

				# Change the turn
				turn = self.turn+1
				self.turn = turn if turn < self.numberOfPlayers else 0

				# Reset the drawn
				player.drawn = False
		print("")

#---------------------------------------------------------------------------------------------------------------------
'''
Function:  playHumanTurn
Purpose:    Find Human player's best move and display it and ask human for input. Play turn accordigly.
Parameters: none
Local Variables: currentPlayer - player with turn, possibleMoves - possible move of players, bestMove - best move of player
'''
#---------------------------------------------------------------------------------------------------------------------

	def playHumanTurn(self):

		# Find player's moves
		currentPlayer = self.players[self.turn]
		possibleMoves = self.findPossibleMoves(currentPlayer)
		bestMove = self.findBestMove(possibleMoves)
		print("----------------------------------------------------------------------------------\n ")

		# Get user input
		print("Player", self.turn)
		userInput = input("Enter your move: ").upper()

		# validate the input
		if re.match('\d{3}\Z', userInput):
			parsedInput = [int(i) for i in userInput]
			if (parsedInput[0], (parsedInput[1], parsedInput[2])) in possibleMoves or (parsedInput[0], (parsedInput[2], parsedInput[1])) in possibleMoves:
				print("Valid Move")

				id, pip1, pip2 = parsedInput[0], parsedInput[1], parsedInput[2]
				endPip = self.players[id].layout.getEndPip()

				# Add tile to appropriate side
				if(pip1 == endPip):
					self.players[id].layout.addDomino((pip1, pip2))
				else:
					self.players[id].layout.addDomino((pip2, pip1))

				# Delete tile from hand
				currentPlayer.hand.deleteDomino((pip1, pip2))

				# Reset the passed
				for player in self.players:
					self.passed[player.id] = False

				# Reset the empty stock count
				self.emptyStockDrawCount = 0

				# Change the turn
				turn = self.turn+1
				self.turn = turn if turn < self.numberOfPlayers else 0

			else:
				print("Invalid Move. Type help for suggestions.")
				#Let human know that move is not valid and ask for help

		elif userInput in ["DRAW", "PASS", "HELP", "SAVE"]:

			#--------------------------------------------------------------------------------------------------------------
			# User asks for help
			if userInput == "HELP":
				if len(possibleMoves):
					print("Possible moves are", possibleMoves)
					print("Best move is", bestMove, "because it has the highest sum out of all possible moves.")
				else:
					print("No moves possible. Please draw or pass if you can't draw.")
			#--------------------------------------------------------------------------------------------------------------
			# User asks for save
			if userInput == "SAVE":

				#get layouts
				l = []
				sc = []
				h = []
				t = []
				s = [list(elem) for elem in self.stock.getStock()]
				ts = self.ts
				r = self.roundNumber
				turn = self.turn

				for player in self.players:
					l.append([list(elem) for elem in player.layout.getLayout()])
					sc.append(player.score)
					h.append([list(elem) for elem in player.hand.getHand()])
					t.append(player.type)

				saveFilename = input("Enter name for your file: ")
				with open(saveFilename, 'w') as outfile:
					json.dump({"TS": ts, "Round": r, "Turn": turn, "Type": t, "Score": sc, "Layout": l, "Hand": h, "Stock": s, "Passed": 0}, outfile)
					exit()



			#--------------------------------------------------------------------------------------------------------------
			# User asks to draw
			if userInput == "DRAW":
				if len(possibleMoves):
					print("You can't draw because moves are possible.")
				else:
					if currentPlayer.drawn:
						print("You can't draw. Pass instead.")
					else:
						if len(self.stock.getStock()):
							# Draw a domino
							currentPlayer.hand.addDomino(self.stock.drawDomino())
							currentPlayer.drawn = True
							print("Player", currentPlayer.id, "drew a domino from stock.")

							# Reset the empty stock count
							self.emptyStockDrawCount = 0

						else:

							# Pass when stock is empty
							self.emptyStockDrawCount += 1
							self.passed[self.turn] = True
							print("Player", currentPlayer.id, "passed as stock is empty.")

							# Change the turn
							turn = self.turn+1
							self.turn = turn if turn < self.numberOfPlayers else 0

							# Reset the drawn
							currentPlayer.drawn = False

			#--------------------------------------------------------------------------------------------------------------
			# User asks to pass
			if userInput == "PASS":
				if len(possibleMoves):
					print("You can't pass because moves are possible.")
				else:
					if currentPlayer.drawn:
						currentPlayer.drawn = False
						currentPlayer.passed = True
						self.passed[self.turn] = True
						print("Player", currentPlayer.id, "passed as the player can't draw twice.")

						# Change the turn
						turn = self.turn+1
						self.turn = turn if turn < self.numberOfPlayers else 0

						# Reset the empty stock count
						self.emptyStockDrawCount = 0

					elif len(self.stock.getStock()) == 0:

						# Pass when stock is empty
						self.emptyStockDrawCount += 1
						self.passed[self.turn] = True
						print("Player", currentPlayer.id, "passed as stock is empty.")

						# Change the turn
						turn = self.turn+1
						self.turn = turn if turn < self.numberOfPlayers else 0

						# Reset the drawn
						currentPlayer.drawn = False

					else:
						print("You can't pass. Draw a domino first")

		else:
			print("Your input is Invalid. Please verify that your input is either MOVE, DRAW, PASS, HELP or SAVE")

		print("----------------------------------------------------------------------------------\n ")


#---------------------------------------------------------------------------------------------------------------------
'''
Function:  checkRoundEnd
Purpose:    Find if round has ended
Parameters: none
Local Variables: returnCode - how rounded ended
'''
#---------------------------------------------------------------------------------------------------------------------
	def checkRoundEnd(self):
		returnCode = 0
		# Check if all players drew and no moves available
		if self.emptyStockDrawCount == self.numberOfPlayers:
			print("Round ended because stock is empty and all no moves available.")
			self.printRoundScores(-1)
			returnCode = 1
		else:
			# Check if empty hand
			for player in self.players:
				if len(player.hand.getHand()) == 0:
					print(player.id, "won the round because hand is empty.")
					self.printRoundScores(player.id)
					returnCode = 1
		return returnCode

#---------------------------------------------------------------------------------------------------------------------
'''
Function:  printRoundScores
Purpose:   Print scores 
Parameters: endCode - how round ended
Local Variables: scores - scores of each player
'''
#---------------------------------------------------------------------------------------------------------------------

	def printRoundScores(self, endCode):
		# Calculate the scores
		scores = []
		for player in self.players:
			hand = player.hand.getHand()
			scores.append(sum([(pair[0]+pair[1]) for pair in hand]))

		# If round ended beacause someone had empty hand
		if endCode != -1:
			self.players[endCode].score += max(scores)
			print("Player", endCode, "won with", max(scores), "points.")

		# If round ended because stock was empty
		else:
			maximumScore = 	max(scores)
			minimumScoreCount = scores.count(min(scores))
			if minimumScoreCount == 1:
				winnerIndex = scores.index(min(scores))
				self.players[winnerIndex].score += max(scores)
				print("Player", winnerIndex, "won with", max(scores), "points.")
			else:
				print("Two or more players have fewest points. The round is a draw.")
		print("\n\nPlayer        \t", "Score\n---------------------------")
		for player in self.players:
			print("Player", player.id, "\t", player.score)

		print("\n\n")
		input("Press any key to continue....")
#---------------------------------------------------------------------------------------------------------------------

main()
