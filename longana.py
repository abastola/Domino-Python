from random import shuffle
import re # regex
import os.path

#---------------------------------------------------------------------------------------------------------------------
class Stock:
	def __init__(self, numberOfPlayers):
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
		print("Player Layout: " + str(self.layout.getLayout()))

#---------------------------------------------------------------------------------------------------------------------

class Round:
	def __init__(self, roundNumber, numberOfHumans, numberOfComputer, scores):
		numberOfPlayers = numberOfHumans + numberOfComputer
		self.roundNumber = roundNumber
		self.numberOfPlayers = numberOfHumans + numberOfComputer
		self.stock = Stock(numberOfPlayers)
		self.players = []
		self.dominoType = 6 if numberOfPlayers == 2 else 9
		self.passed = []
		self.turn = 0
		self.emptyStockDrawCount = 0

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

	def printRoundDetails(self):
		for player in self.players:
			player.printPlayerDetails()

	def findAndPlaceEngine(self):
		engine = self.dominoType - self.roundNumber
		engineFound = False
		playerWithEngine = -1
		print(engine)
		print(self.stock.getStock())
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
					player.hand.addDomino(self.stock.drawDomino())
			self.printRoundDetails()

		self.turn = playerWithEngine
		
		# Change the turn
		turn = self.turn+1
		self.turn = turn if turn < self.numberOfPlayers else 0
		
		return playerWithEngine

	def beginRound(self):
		
		while True:
			
			# Play Turn based on type of player
			if self.players[self.turn].type == "Computer":
				self.playComputerTurn()
			else:
				self.playHumanTurn()
			
			# Print board after player's move
			self.printRoundDetails()

			#check if round has ended
			returnCode = self.checkRoundEnd()

			if returnCode == 1:
				scores = []
				for player in self.players:
					scores.append(player.score)
				return scores

			print("----------------------------------------------------------------------------------\n ")

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

	def playComputerTurn(self):
		
		# Find player's move
		currentPlayer = self.players[self.turn]
		possibleMoves = self.findPossibleMoves(currentPlayer)
		bestMove = self.findBestMove(possibleMoves)
		
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

			print("Player", self.turn, "placed", pip1, pip2, "on side", id)
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

		# Pass or draw a tile
		else:
			
			#try to draw a tile
			self.drawOrPass(currentPlayer)
	
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

	def playHumanTurn(self):

		# Find player's moves
		currentPlayer = self.players[self.turn]
		possibleMoves = self.findPossibleMoves(currentPlayer)
		bestMove = self.findBestMove(possibleMoves)
		
		# Print Player details
		print("Turn ID:", currentPlayer.id)
		print("Possible Moves:", possibleMoves)
		print("Best Move:", bestMove)
		print("Stock:", self.stock.getStock() , "\n")

		# Get user input
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
						currentPlayer.passed = False
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

			self.printRoundDetails()
#---------------------------------------------------------------------------------------------------------------------

def main():
	print("-"*75)
	print(" "*33, "Welcome", " "*33)
	print("-"*75)
	
	gameType = ""
	tournamentScore = -1
	roundNumber = 0
	humanPlayer = 0
	computerPlayer = 0

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
			if humanPlayer >= 0 and humanPlayer < 4:
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

	else:
		while True:
			fileName = input("Enter the filname you want to load: ")
			if os.path.exists(fileName):
				break
			else:
				print("File doesn't exist.")

	#input("pause")

	totalPlayer = humanPlayer + computerPlayer
	maximumRound = 7 if totalPlayer <= 2 else 9
	scores = [0, 0, 0, 0]
	
	while True:
		# Begin the round
		round = Round(roundNumber, humanPlayer, computerPlayer, scores)
		
		# Print who placed the round
		print("Player", round.findAndPlaceEngine(), "placed the engine.")
		
		# Print the round detauls
		round.printRoundDetails()

		# Start the round
		scores = round.beginRound()

		print(scores)

		round.printRoundDetails()

		if max(scores) > tournamentScore:
			break

		temp = roundNumber
		roundNumber = temp + 1 if roundNumber < maximumRound else 0

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

main()