import random
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Updated Dice face mappings with Unicode symbols
RING_DIE = [
    "d6 — Blank \u25a2",  
    "d6 — Opportunity with Strife \u2731 \U0001F525",      
    "d6 — Opportunity \u2731", 
    "d6 — Success with Strife \u2714 \U0001F525",  
    "d6 — Success \u2714",   
    "d6 — Explosive Success with Strife \U0001F4A5 \U0001F525"  
]

SKILL_DIE = [
    "d12 — Blank \u2b20", 
    "d12 — Blank \u2b20",
    "d12 — Opportunity \u2731", 
    "d12 — Opportunity \u2731", 
    "d12 — Opportunity \u2731",
    "d12 — Success with Strife \u2714 \U0001F525", 
    "d12 — Success with Strife \u2714 \U0001F525",  
    "d12 — Success \u2714", 
    "d12 — Success \u2714",  
    "d12 — Success with Opportunity \u2714 \u2731",  
    "d12 — Explosive Success with Strife \U0001F4A5 \U0001F525",
    "d12 — Explosive Success \U0001F4A5"    
]

# Store user data in a dictionary, keyed by user ID
user_data = {}

def get_user_data(user_id, user_name):
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user_name,  # Default to the user's Telegram name
            'current_roll': [],
            'kept_dice': [],
            'explosions': {},
            'has_kept': False
        }
    return user_data[user_id]

def roll_ring_die():
    return RING_DIE[random.randint(0, 5)]

def roll_skill_die():
    return SKILL_DIE[random.randint(0, 11)]

def is_ring_die(die):
    return die in RING_DIE

def is_skill_die(die):
    return die in SKILL_DIE

def format_roll_result(roll):
    result_lines = []
    for i, result in enumerate(roll):
        index = str(i + 1)
        result_lines.append(f"{index}. {result}")
    return "\n".join(result_lines)

def format_kept_result(kept_dice, explosions):
    result_lines = []
    for i, result in enumerate(kept_dice):
        index = str(i + 1)
        result_lines.append(f"{index}. {result}")
        if index in explosions:
            for j, explosion_result in enumerate(explosions[index], 1):
                result_lines.append(f"{index}.{j} {explosion_result}")
    return "\n".join(result_lines)

def roll_dice(update: Update, ring_dice, skill_dice):
    user_roll_data = get_user_data(update.message.from_user.id, update.message.from_user.first_name)
    user_roll_data['current_roll'] = [roll_ring_die() for _ in range(ring_dice)] + [roll_skill_die() for _ in range(skill_dice)]
    user_roll_data['has_kept'] = False
    user_roll_data['explosions'] = {}
    result_message = f"{user_roll_data['name']} rolled:\n" + format_roll_result(user_roll_data['current_roll'])
    update.message.reply_text(result_message, parse_mode='Markdown')

def parse_and_roll_or_add(update: Update, args, add=False):
    if len(args) == 0:
        if add:
            update.message.reply_text("Usage: /add or /a XbYw (where X is the number of Ring dice and Y is the number of Skill dice to add)")
        else:
            update.message.reply_text("Usage: /roll or /r XbYw (where X is the number of Ring dice and Y is the number of Skill dice)")
        return

    match = re.match(r"(\d+)b(\d+)w", args[0])
    if match:
        ring_dice = int(match.group(1))
        skill_dice = int(match.group(2))
        if add:
            add_dice(update, ring_dice, skill_dice)
        else:
            roll_dice(update, ring_dice, skill_dice)
    else:
        if add:
            update.message.reply_text("Invalid format. Use XbYw, where X is the number of Ring dice and Y is the number of Skill dice to add.")
        else:
            update.message.reply_text("Invalid format. Use XbYw, where X is the number of Ring dice and Y is the number of Skill dice.")

def add_dice(update: Update, ring_dice, skill_dice):
    user_roll_data = get_user_data(update.message.from_user.id, update.message.from_user.first_name)
    if not user_roll_data['current_roll']:
        update.message.reply_text("You must roll dice before adding more.")
        return
    user_roll_data['current_roll'] += [roll_ring_die() for _ in range(ring_dice)] + [roll_skill_die() for _ in range(skill_dice)]
    result_message = f"{user_roll_data['name']} added:\n" + format_roll_result(user_roll_data['current_roll'])
    update.message.reply_text(result_message, parse_mode='Markdown')

def reroll_dice(update: Update, context: CallbackContext):
    user_roll_data = get_user_data(update.message.from_user.id, update.message.from_user.first_name)
    if not user_roll_data['current_roll']:
        update.message.reply_text("You must roll dice before rerolling.")
        return

    args = context.args
    if len(args) == 0:
        update.message.reply_text("Usage: /reroll or /rr indices (space/-separated list of dice indices to reroll)")
        return

    for index in args:
        if '.' in index:
            # Handle exploded dice reroll
            original_index, explosion_index = map(int, index.split('.'))
            original_index -= 1
            explosion_index -= 1
            original_index_str = str(original_index + 1)

            if original_index_str in user_roll_data['explosions'] and 0 <= explosion_index < len(user_roll_data['explosions'][original_index_str]):
                die_to_reroll = user_roll_data['explosions'][original_index_str][explosion_index]
                if is_ring_die(die_to_reroll):
                    user_roll_data['explosions'][original_index_str][explosion_index] = roll_ring_die()
                else:
                    user_roll_data['explosions'][original_index_str][explosion_index] = roll_skill_die()
        else:
            # Handle original dice reroll
            i = int(index) - 1
            if 0 <= i < len(user_roll_data['current_roll']):
                die_to_reroll = user_roll_data['current_roll'][i]
                if is_ring_die(die_to_reroll):
                    user_roll_data['current_roll'][i] = roll_ring_die()
                else:
                    user_roll_data['current_roll'][i] = roll_skill_die()

    result_message = f"{user_roll_data['name']} rerolled:\n" + format_roll_result(user_roll_data['current_roll'])
    update.message.reply_text(result_message, parse_mode='Markdown')

def keep_dice(update: Update, context: CallbackContext):
    user_roll_data = get_user_data(update.message.from_user.id, update.message.from_user.first_name)
    if not user_roll_data['current_roll']:
        update.message.reply_text("You must roll dice before keeping them.")
        return

    args = context.args
    if len(args) == 0:
        update.message.reply_text("Usage: /keep or /k indices (space/-separated list of dice indices to keep). Use '0' to keep no dice.")
        return

    if args[0] == '0':
        user_roll_data['kept_dice'] = []
        result_message = "No dice kept."
    else:
        kept_dice = []
        explosions_to_keep = {}
        
        for arg in args:
            if '.' in arg:
                original_index, explosion_index = map(int, arg.split('.'))
                original_index -= 1  # Convert to 0-based index
                explosion_index -= 1  # Convert to 0-based index
                original_index_str = str(original_index + 1)
                if original_index_str in user_roll_data['explosions']:
                    if explosion_index < len(user_roll_data['explosions'][original_index_str]):
                        if original_index_str not in explosions_to_keep:
                            explosions_to_keep[original_index_str] = []
                        explosions_to_keep[original_index_str].append(user_roll_data['explosions'][original_index_str][explosion_index])
            else:
                index = int(arg) - 1  # Convert to 0-based index
                if 0 <= index < len(user_roll_data['current_roll']):
                    kept_dice.append(user_roll_data['current_roll'][index])

        user_roll_data['kept_dice'] = kept_dice
        user_roll_data['explosions'] = explosions_to_keep
        result_message = f"{user_roll_data['name']} kept:\n" + format_kept_result(user_roll_data['kept_dice'], user_roll_data['explosions'])
    
    user_roll_data['has_kept'] = True  # Set the flag indicating dice have been kept
    update.message.reply_text(result_message, parse_mode='Markdown')

def remove_dice(update: Update, context: CallbackContext):
    user_roll_data = get_user_data(update.message.from_user.id, update.message.from_user.first_name)
    if not user_roll_data['current_roll'] and not user_roll_data['explosions']:
        update.message.reply_text("You must roll dice before removing them.")
        return

    args = context.args
    if len(args) == 0:
        update.message.reply_text("Usage: /remove or /rm indices (space/-separated list of dice indices to remove)")
        return

    for arg in args:
        if '.' in arg:
            # Handle removal of exploded dice
            original_index, explosion_index = map(int, arg.split('.'))
            original_index -= 1  # Convert to 0-based index
            explosion_index -= 1  # Convert to 0-based index
            original_index_str = str(original_index + 1)

            if original_index_str in user_roll_data['explosions']:
                if 0 <= explosion_index < len(user_roll_data['explosions'][original_index_str]):
                    del user_roll_data['explosions'][original_index_str][explosion_index]

                    # If there are no more explosions for this die, remove the entry
                    if not user_roll_data['explosions'][original_index_str]:
                        del user_roll_data['explosions'][original_index_str]
        else:
            # Handle removal of original dice
            index = int(arg) - 1  # Convert to 0-based index
            if 0 <= index < len(user_roll_data['current_roll']):
                del user_roll_data['current_roll'][index]

                # Also remove any associated explosions if the original die is removed
                index_str = str(index + 1)
                if index_str in user_roll_data['explosions']:
                    del user_roll_data['explosions'][index_str]

    result_message = f"{user_roll_data['name']} remaining:\n" + format_roll_result(user_roll_data['current_roll'])
    if user_roll_data['explosions']:
        result_message += "\nExploded:\n" + format_kept_result([], user_roll_data['explosions'])

    update.message.reply_text(result_message, parse_mode='Markdown')

def explode_dice(update: Update, context: CallbackContext):
    user_roll_data = get_user_data(update.message.from_user.id, update.message.from_user.first_name)
    if not user_roll_data['current_roll']:
        update.message.reply_text("You must roll dice before exploding them.")
        return

    if not user_roll_data['has_kept']:
        update.message.reply_text("You need to keep dice before you can explode them.")
        return

    args = context.args
    if len(args) == 0:
        update.message.reply_text("Usage: /explode or /e indices (space/-separated list of dice indices to explode)")
        return

    for index in args:
        if '.' in index:
            # Handle explosion of already exploded dice
            original_index, explosion_index = map(int, index.split('.'))
            original_index -= 1
            explosion_index -= 1
            original_index_str = str(original_index + 1)

            if original_index_str in user_roll_data['explosions'] and 0 <= explosion_index < len(user_roll_data['explosions'][original_index_str]):
                die_to_explode = user_roll_data['explosions'][original_index_str][explosion_index]
                if '\U0001F4A5' in die_to_explode:
                    if is_ring_die(die_to_explode):
                        user_roll_data['explosions'][original_index_str].append(roll_ring_die())
                    else:
                        user_roll_data['explosions'][original_index_str].append(roll_skill_die())
        else:
            # Handle explosion of original dice
            i = int(index) - 1
            index_str = str(i + 1)
            if 0 <= i < len(user_roll_data['kept_dice']) and '\U0001F4A5' in user_roll_data['kept_dice'][i]:
                die_to_explode = user_roll_data['kept_dice'][i]
                if index_str not in user_roll_data['explosions']:
                    user_roll_data['explosions'][index_str] = []
                if is_ring_die(die_to_explode):
                    user_roll_data['explosions'][index_str].append(roll_ring_die())
                else:
                    user_roll_data['explosions'][index_str].append(roll_skill_die())

    result_message = f"{user_roll_data['name']} after explosion:\n" + format_kept_result(user_roll_data['kept_dice'], user_roll_data['explosions'])
    update.message.reply_text(result_message, parse_mode='Markdown')

def finalize_result(update: Update, context: CallbackContext):
    user_roll_data = get_user_data(update.message.from_user.id, update.message.from_user.first_name)
    if not user_roll_data['has_kept']:
        update.message.reply_text("You need to keep dice before finalizing the result.")
        return
    
    successes = 0
    opportunities = 0
    strife = 0
    
    for die in user_roll_data['kept_dice']:
        if "\u2714" in die:  # Success
            successes += 1
        if "\U0001F4A5" in die:  # Explosive Success counts as a Success as well
            successes += 1
        if "\u2731" in die:  # Opportunity
            opportunities += 1
        if "\U0001F525" in die:  # Strife
            strife += 1

    for index, explosions_list in user_roll_data['explosions'].items():
        for explosion_result in explosions_list:
            if "\u2714" in explosion_result:  # Success
                successes += 1
            if "\U0001F4A5" in explosion_result:  # Explosive Success counts as a Success as well
                successes += 1
            if "\u2731" in explosion_result:  # Opportunity
                opportunities += 1
            if "\U0001F525" in explosion_result:  # Strife
                strife += 1

    result_message = (f"Final Results for {user_roll_data['name']}:\n"
                      f"Successes: {successes} \u2714\n"
                      f"Opportunities: {opportunities} \u2731\n"
                      f"Strife: {strife} \U0001F525")
    update.message.reply_text(result_message, parse_mode='Markdown')

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("""
*Dice Symbols*:
— Success: ✔
— Opportunity: ✱
— Strife: 🔥
— Explosive Success: 💥

*Available commands* \(full and short versions\):
• /name or /n <character name\> — Sets your character's name, which will be displayed with each roll result\.
• /roll or /r XbYw — Rolls X Ring dice and Y Skill dice\.
• /add or /a XbYw — Adds X Ring dice and Y Skill dice to the current roll\.
• /reroll or /rr <indices\> — Rerolls the dice at the given indices\.
• /keep or /k <indices\> — Keeps the dice at the given indices\. Use '0' to keep no dice\.
• /remove or /rm <indices\> — Removes the dice at the given indices\.
• /explode or /e <indices\> — Explodes the dice at the given indices if they have an Explosive Success\.
• /finalize or /f — Finalizes the result and displays the number of Successes, Opportunities, and Strife\.
• /rule or /rules — Explains the meaning of each dice symbol in L5R 5e\.
• /probability or /p XbYw TN — Simulates and calculates the chances of successfully passing a check of a given TN with XbYw dice\.
• /help or /h — Displays this help message\.
• /quit — Exits the application\.

*Bot by*: Eugene T\. \(@Lelouch\_Vee\)\. No rights reserved \(CC Zero Universal 1\.0\)

_Legend of the Five Rings, the L5R logo, and the white FFG logo are trademarks of Fantasy Flight Games\._ 
""", parse_mode='MarkdownV2')

def rule_command(update: Update, context: CallbackContext):
    update.message.reply_text("""
Dice Roll Sequence:
1. *Declare intention*: Tell the GM what you're trying to achieve
2. *Determine details*: GM chooses skill, ring and TN for the roll
3. *Assemble dice pool and ROLL*: Roll number of Ring dice equal to chosen ring, and Skill dice equal to chosen Skill.
4. *Reroll or add*: Reroll, add or remove dice due to advantages, disadvantages, or abilities.
4. *Keep*: Chose a number of dice equal to used Ring to keep
5. *Resolve*: Apply effects from, in this order: Explosive Successes 💥, Strife 🔥, Opportunity ✱, Total Successes (✔/💥).

Resolving Symbols on Kept Dice:
The player processes symbols from the kept dice results in the following sequence to determine the check's outcome:
1.  *Explosive Success* (💥): For each 💥, the player may roll an additional die of the same type and decide whether to keep or discard it.
2.  *Strife* (🔥): The character gains 1 strife for each 🔥. Strife affects character's emotional state and abilities.
3.  *Opportunity* (✱): Use ✱ to introduce additional story details, special effects and activation of character abilities .
4.  *Total Successes* (✔️ / 💥): If the total ✔️ and 💥 meets or exceeds the TN, the character succeeds.
""", parse_mode='Markdown')

def set_name(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if len(context.args) == 0:
        update.message.reply_text("Usage: /name <character_name> - Sets your character's name.")
        return

    new_name = " ".join(context.args)
    user_roll_data = get_user_data(user_id, user_name)
    user_roll_data['name'] = new_name

    update.message.reply_text(f"Your character's name has been set to: {new_name}", parse_mode='Markdown')

def calculate_probability(ring_dice, skill_dice, tn, simulations=100000):
    def roll_die(die_faces):
        result = random.choice(die_faces)
        return result

    successes_needed = tn
    success_count = 0

    for _ in range(simulations):
        successes = 0
        dice_pool = [roll_ring_die() for _ in range(ring_dice)] + [roll_skill_die() for _ in range(skill_dice)]
        keep_count = 0

        while dice_pool and keep_count < (ring_dice + skill_dice):
            die_result = dice_pool.pop(0)
            if "\u2714" in die_result:  # Success
                successes += 1
            if "\U0001F4A5" in die_result:  # Explosive Success
                successes += 1
                if is_ring_die(die_result):
                    dice_pool.append(roll_ring_die())
                else:
                    dice_pool.append(roll_skill_die())
            keep_count += 1

        if successes >= successes_needed:
            success_count += 1

    probability = success_count / simulations
    return probability

def probability_command(update: Update, context: CallbackContext):
    args = context.args
    if len(args) != 2:
        update.message.reply_text("Usage: /probability or /p XbYw TN (e.g., /probability 3b2w 4)")
        return

    match = re.match(r"(\d+)b(\d+)w", args[0])
    if match:
        ring_dice = int(match.group(1))
        skill_dice = int(match.group(2))
        tn = int(args[1])
        probability = calculate_probability(ring_dice, skill_dice, tn)
        update.message.reply_text(f"Probability of achieving TN {tn} with {ring_dice} Ring dice and {skill_dice} Skill dice: {probability:.2%}", parse_mode='Markdown')
    else:
        update.message.reply_text("Invalid format. Use XbYw for dice and TN for target number (e.g., /probability 3b2w 4).")


def main():
    # Insert your bot's API key here
    updater = Updater("YOUR KEY GOES HERE", use_context=True)
    dp = updater.dispatcher

    # Registering command handlers with full and short versions
    dp.add_handler(CommandHandler(["help", "h"], help_command))
    dp.add_handler(CommandHandler(["roll", "r"], lambda update, context: parse_and_roll_or_add(update, context.args)))
    dp.add_handler(CommandHandler(["add", "a"], lambda update, context: parse_and_roll_or_add(update, context.args, add=True)))
    dp.add_handler(CommandHandler(["reroll", "rr"], reroll_dice))
    dp.add_handler(CommandHandler(["keep", "k"], keep_dice))
    dp.add_handler(CommandHandler(["remove", "rm"], remove_dice))
    dp.add_handler(CommandHandler(["explode", "e"], explode_dice))
    dp.add_handler(CommandHandler(["finalize", "f"], finalize_result))
    dp.add_handler(CommandHandler(["rule", "rules"], rule_command))
    dp.add_handler(CommandHandler(["name", "n"], set_name))
    dp.add_handler(CommandHandler(["probability", "p"], probability_command))
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
