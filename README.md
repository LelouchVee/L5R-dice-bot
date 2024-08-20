![Explosive success!](/resources/skill_exp_str.png "Explosive success") ![Five Rings!](/resources/l5r_logo.png "Five Rings") ![Full of opportunity!](/resources/ring_opp.png "Opportunity")

# L5R Dice Roller Telegram Bot

A Telegram bot for rolling of the Narrative Dice for Legend of the Five Rings (L5R) 5th Edition role-playing game by FFG. 

This bot simulates the rolling of L5R dice, including handling special mechanics like exploding successes, advantages, and disadvantages. It also includes features for calculating probabilities of success in various scenarios.

## Features

- Dice Rolling: Roll a combination of Ring and Skill dice using the XbYw format.
- Exploding Dice: Automatically handles the L5R mechanic of rolling additional dice on explosive successes.
- Rerolling: Allows rerolling of dice before deciding which ones to keep.
- Advantages & Disadvantages: Adjust probabilities by rerolling based on character advantages (reroll up to two dice without successes) or disadvantages (reroll up to two dice with successes).
- Probability Calculation: Calculate the probability of achieving a given Target Number (TN) with a specific combination of Ring and Skill dice.
- Character Naming: Set a character name to personalize your roll outputs.
- Finalization: Finalize your roll to count successes, opportunities, and strife.

Tracking of names and rolls is performed separately for each user by their profile name.

Additionally, /resources folder provides all the necessary dice faces and symbols as separate .png files intended for use with the bot - but currently unavaible for actual use in realistic conditions due to Telegram's limitation of custom emoji to Fragment-enabled bots.

## Commands

+ /name or /n <Character \Name>

Sets user's character name, which will be displayed with each roll result.

+ /roll or /r <XbYw>

Rolls X Ring dice and Y Skill dice. Use the XbYw format to specify the number of each dice type.

+ /add or /a <XbYw>

Adds additional Ring and Skill dice to the current roll.

+ /reroll or /rr <indices>

Rerolls the dice at the specified indices (1-based). Can reroll both original and exploded dice.

+ /keep or /k <indices>

Keeps the dice at the specified indices (1-based). Use 0 to keep no dice.

+ /remove or /rm <indices>

Removes the dice at the specified indices (1-based).

+ /explode or /e <indices>

Explodes the dice at the specified indices (1-based) if they have an Explosive Success. The additional dice rolled do not count towards the Ring dice keep limit.

+ /finalize or /f
  
Finalizes the result and displays the total number of Successes, Opportunities, and Strife.

+ /probability or /p <XbYw TN [-a] [-d]>
  
Calculates the probability of achieving a specified Target Number (TN) with X Ring dice and Y Skill dice. Use the -a flag for advantage (rerolling up to two dice without successes) and the -d flag for disadvantage (rerolling up to two dice with successes).

+ /name or /n <character_name>

Sets your character's name, which will be displayed with each roll result.

+ /help or /h
  
Displays the list of available commands and their descriptions.

+ /rule or /rules

Explains the meaning of each dice symbol in L5R 5e and the sequence of a dice roll.

## Deployment

TBD

## Usage

Once the bot is running, add it to your Telegram group or start a chat with it directly. Use the commands described above to roll dice, calculate probabilities, and manage your L5R game sessions.

Main branch version of this bot is currently self-hosted and available at https://t.me/l5r_dice_bot

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under CC Zero universal 1.0

Legend of the Five Rings, the L5R logo, and the white FFG logo are trademarks of Fantasy Flight Games.
