import random
import string

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

words = []

def get_welcome_response():
    global words
    
    session_attributes = {
        "difficulty" : 2,
        "current_letters" : '',
        "min_letters" : 4,
        "started" : False,
    }
    
    card_title = "Welcome"
    speech_output = "Welcome to Superghost. Would you like to go first?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Would you like to go first?"
    #session_attributes["words"] = initialize_dictionary("scrabble_words.txt")
    words = initialize_dictionary("scrabble_words.txt")
    
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def explain_rules(intent, session):
    card_title = intent['name']
    should_end_session = False
    session_attributes = session["attributes"]
    
    speech_output = "This is a word-building game where each player takes turns saying a letter. "\
                    "The goal is to always work towards the completion of a word without being the one "\
                    "to complete it. For example, if B, A, K has been played you could play I to work "\
                    "towards the word baking, but not E as it would complete the word bake."
    
    reprompt_text = "If you'd like to hear the rules again just say so!"
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def validate_move(intent, session):
    global words
    session_attributes = session["attributes"]
    
    card_title = intent['name']
    should_end_session = False
    reprompt_text = "..."
    
    if session_attributes["started"] == False:
        speech_output = "I think I misunderstood you."
        reprompt_text = "Please tell me if you wanted to go first."
    elif 'Letter' in intent['slots']:
        proposed_move = session_attributes["current_letters"] + intent["slots"]["Letter"]["value"][0].lower()
        valid = False
        for word in words:
            if word.startswith(proposed_move):
                valid = True
                break
        if not valid:
            old_move = proposed_move[:-1]
            thinking_of = "memes"
            for word in words:
                if word.startswith(old_move):
                    thinking_of = word
                    break
            speech_output = "I don't know any words starting with {}. I win! I was thinking of {}".format(proposed_move, thinking_of)
            should_end_session = True
            
        elif len(proposed_move) >= session_attributes["min_letters"] and proposed_move in words:
            # Invalid move! It made a word we know...
            speech_output = "You made the word {}! I win this time.".format(proposed_move)
            should_end_session = True
        else:
            session_attributes['current_letters'] = proposed_move
            my_move = get_letter_pick(session_attributes)
            if my_move is None:
                speech_output = "I give up!"
                should_end_session = True
            else:
                full_word = proposed_move + my_move
                session_attributes['current_letters'] = full_word
                speech_output = "My move is {} to make {}".format(my_move.upper(), " ".join([letter.upper() for letter in full_word]))
                should_end_session = False
    else:
        speech_output = "I'm not sure what your move is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your letter is. " \
                        "You can tell me your move by saying, for example, " \
                        "my letter is J."
        should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#def set_difficulty(intent, session):
#    pass
    
def respond_to_bluff_call(intent, session):
    global words
    session_attributes = session["attributes"]
    
    card_title = intent['name']
    should_end_session = True
    
    if len(session_attributes['current_letters']) >= session_attributes["min_letters"] and session_attributes['current_letters'] in words:
        speech_output = "You're right, {} is already a word! You win.".format(session_attributes['current_letters'])
        reprompt_text = "..."
    else:
        valid = False
        for word in words:
            if word.startswith(session_attributes['current_letters']):
                valid = True
                speech_output = "Nope, I was thinking of the word {}. I win!".format(word)
                reprompt_text = "..."
        if not valid:
            speech_output = "You got me. I lose!"
            reprompt_text = "..."
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def respond_to_go_first(intent,session):
    session_attributes = session["attributes"]
    
    card_title = intent['name']
    should_end_session = False
    
    if session_attributes['started'] == True:
        speech_output = "I think I misunderstood you."
        reprompt_text = "Please give me a letter."
    elif 'First' in intent['slots']:
        session_attributes['started'] = True
        if intent['slots']['First']['value'].lower() in ["yes","yeah","ok","sure"]:
            speech_output = "OK, you go first. " \
                            "Let me know what letter you want to start with."
            reprompt_text = "Give me a letter!!"
        else:
            shufflebet = list(string.ascii_lowercase) 
            random.shuffle(shufflebet)
            first_move = shufflebet[0]
            
            session_attributes['current_letters'] = first_move
            
            speech_output = "OK, I'll go first. "\
                            "Our first letter will be {}".format(first_move.upper())
            reprompt_text = "I said said the first letter is {}. I'ts your move now.".format(first_move.upper())
            
    else:
        speech_output = "I didn't catch that " \
                        "Do you want to go first?"
        reprompt_text = "I said do you want to go first!?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# ----- My Helpers

def get_letter_pick(session_attributes):
    global words
    word_frag = session_attributes["current_letters"]
    difficulty = session_attributes["difficulty"]
    min_letters = session_attributes["min_letters"]
    
    # TODO: Change the dictionary we check against to be difficulty-specific
    # TODO: Add bluffs at certain difficulties

    shufflebet = list(string.ascii_lowercase) 
    random.shuffle(shufflebet)
    shufflebet = "".join(shufflebet)

    if difficulty >= 2:
        bluff = True
    else:
        bluff = False

    for letter in shufflebet:
        trial_move = word_frag + letter
        print(trial_move)

        for word in words:
            if word.startswith(trial_move) \
              and (len(word) > len(trial_move)) \
              and (len(word) >= min_letters):
                if difficulty < 1:
                    return letter
                else:
                    match = False
                    for word in words:
                        if word == trial_move:
                            match = True
                            break
                    if not match:
                        return letter
    
    # No moves!!
    if bluff:
        # For now, just make a random move!
        print("Bluffing!")
        return shufflebet[0]
    else:
        return None
        
def initialize_dictionary(fname="scrabble_words.txt"):
    words = []
    
    # TEMP
    #return ["dogs", "aaaaa", "reea"] 
    
    with open(fname,'r') as f:
        for line in f.readlines():
            to_add = True
            for letter in line.strip().lower():
                if letter not in string.ascii_lowercase:
                    to_add = False
                    break
            if to_add:
                words.append(line.strip().lower())
    return words

# --------------- Events ------------------
        
def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MyLetterIsIntent":
        return validate_move(intent, session)
    #elif intent_name == "SetDifficultyIntent":
    #    return set_difficulty(intent, session)
    elif intent_name == "CallYourBluffIntent":
        return respond_to_bluff_call(intent,session)
    elif intent_name == "GoFirstIntent":
        return respond_to_go_first(intent,session)
    elif intent_name == "ExplainRulesIntent":
        return explain_rules(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
