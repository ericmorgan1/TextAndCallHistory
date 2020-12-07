import csv
import datetime
import time

# Configuration...
CALL_HISTORY_FILE_NAME = "call-history.csv"
TEXT_HISTORY_FILE_NAME = "text-messages.txt"
PHONE_NUMBER = ""
TEXT_SENDER_NAME = ""
OUTPUT_FILE = "timeline/timeline.html"

###
# Classes
###

class CommunicationEvent:
    def __init__(self, eventType, dateTime):
        self.Type = eventType     # 1 = Phone, 2 = Text Message
        self.DateTime = dateTime

        # Phone data...
        self.PhoneContactName = ""
        self.PhoneNumber = ""
        self.PhoneDurationSeconds = 0
        self.PhoneCallType = ""

        # Test Message data...
        self.TextSenderName = ""
        self.TextContents = ""

    def __str__(self):
        if (self.Type == 1):
            durationMinutes = self.PhoneDurationSeconds / 60
            return "Phone: {0}, {1}, {2}, {3:6.1f} minutes, {4}".format(self.DateTime, self.PhoneContactName, self.PhoneNumber, durationMinutes, self.PhoneCallType)
        elif (self.Type == 2):
            return "Text: {0}, {1}, {2}".format(self.DateTime, self.TextSenderName, self.TextContents)
        else:
            return "???"

##############################
# Support Functions...
##############################

# Returns true if the given phone number matches the "match" provided...
def doesPhoneNumberMatch(phoneNumber, match):
    return match in phoneNumber

# Converts the "duration" string to a number of seconds...
def convertDurationStringToSeconds(duration):
    x = time.strptime(duration,'%H:%M:%S')
    return datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()

##############################
# PHONE CALL FUNCTIONS
##############################

# Parses a phone call file into an array of CommunicationEvent objects. Filters by phoneNumberToFilter...
def parsePhoneCallFile(fileName,phoneNumberToFilter):
    events = []
    with open(fileName) as csvFile:
        csvReader = csv.reader(csvFile)
        next(csvReader) # Skip header

        # Parse phone data. If the number doesn't match, skip it...
        for row in csvReader:        
            phoneData = parsePhoneCallLine(row)
            if (not(doesPhoneNumberMatch(phoneData.PhoneNumber, phoneNumberToFilter))): continue
            events.append(phoneData)
    return events

# Parses a CSV line from a phone call log and returns a CommunicationEvent
def parsePhoneCallLine(row):
    event = CommunicationEvent(1, parsePhoneCallDate(row[2]))    
    event.PhoneContactName = row[0].strip()
    event.PhoneNumber = row[1]
    event.PhoneDurationSeconds = convertDurationStringToSeconds(row[3])
    event.PhoneCallType = row[4]
    return event

# Parses the date string from a phone call into a datetime object...
def parsePhoneCallDate(sDate):
    sDate = sDate.split(".")[0] # Strip off milliseconds
    dOrig = datetime.datetime.strptime(sDate, "%Y-%m-%dT%H:%M:%S")
    dAdj = dOrig + datetime.timedelta(hours = -6)   # Adjust for Central time
    return dAdj

##############################
# TEXT MESSAGE FUNCTIONS
##############################

# Parses a text message file into an array of CommunicationEvent objects
def parseTextMessageFile(fileName):
    lines = parseTextMessageFileIntoLines(fileName)
    
    events = []
    for line in lines:
        events.append(parseTextMessageLine(line))
    return events

# Parses a text message file into individual lines
def parseTextMessageFileIntoLines(fileName):
    # Open file...
    file = open(fileName,"r",encoding='utf-8')

    # Skip first two lines because contain info we don't need...
    file.readline()
    file.readline()

    # Read data into an array. We need to account for newlines, so consider lines starting with "[" to be the start of a new message
    lines = []
    currentLine = ""
    for line in file:
        if line.startswith("["):
            if (len(currentLine) > 0): lines.append(currentLine)
            currentLine = line
        else:
            currentLine += line
    return lines

# Parses a text line from a text message log and returns a CommunicationEvent
def parseTextMessageLine(line):

    # Sometimes messages appear like "Me: " and sometimes like "Me : ". So try both ways.
    cIndex = 0; cSkipAmount = 0
    if (" : " in line): cIndex = line.index(" : "); cSkipAmount = 2
    elif (": " in line): cIndex = line.index(": "); cSkipAmount = 2

    # Gather data...
    sDateTime = line[line.index("[")+1 : line.index("]")]
    contents = line[cIndex+cSkipAmount:]
    sender = line[line.index("] ")+2 : cIndex]

    # Create the event...
    event = CommunicationEvent(2, parseTextMessageDate(sDateTime))
    event.TextSenderName = sender
    event.TextContents = contents
    return event

# Parses the date string from a text message call into a datetime object...
def parseTextMessageDate(sDate):
    return datetime.datetime.strptime(sDate, "%m/%d/%y, %I:%M %p")

##############################
# HTML GENERATION FUNCTIONS
##############################

# Generates the full HTML for all the events...
def genHTMLForEvents(events, textSenderName):
    html = genHTMLStartFile()
    
    html += '<div class="chat">'

    currentDay = 0; currentMonth = 0;
    for event in events:
        # If we are on a new month/day, print out the day and update
        if (event.DateTime.day != currentDay or event.DateTime.month != currentMonth):
            html += '<span class="new-day">{0}</span>'.format(event.DateTime.strftime("%A, %b %d, %Y"))
            currentDay = event.DateTime.day
            currentMonth = event.DateTime.month
        
        if (event.Type == 1): html += genHTMLForPhoneEvent(event)
        elif (event.Type == 2): html += genHTMLForTextEvent(event, textSenderName)
    html += '</div>'
    
    html += genHTMLEndFile()
    return html

# Generates the HTML for the beginning of the file...
def genHTMLStartFile():
    return """
    <html>
    <head>
        <link rel="stylesheet" href="css/styles.css">
        <link rel="stylesheet" href="css/all.min.css">
    </head>
    
    <body>
    """
    
# Generates the HTML for the end of the file...
def genHTMLEndFile():
    return """
    </body>
    </html>
    """

# Generates HTML for a single Phone CommuncationEvent
def genHTMLForPhoneEvent(phoneEvent):
    className = "call missed-call" if (phoneEvent.PhoneCallType == "Missed") else "call"
    iconName = "fas fa-phone-slash" if (phoneEvent.PhoneCallType == "Missed") else "fas fa-phone"
    date = phoneEvent.DateTime.strftime("%b %d, %Y, %I:%M %p")
    callType = phoneEvent.PhoneCallType
    durationMinutes = phoneEvent.PhoneDurationSeconds / 60
    
    html = '<div class="' + className + '">'
    html += '<i class="' + iconName + '"></i>'
    html += '<span> {0}; Duration: {1:3.1f} minutes</span>'.format(callType, durationMinutes)
    html += '<div class="call-date">{0}; {1}</div>'.format(phoneEvent.PhoneNumber, phoneEvent.PhoneContactName)
    html += '<div class="call-date">' + date + '</div>'
    html += '</div>'    
    return html

# Generates HTML for a single Text Message CommuncationEvent
def genHTMLForTextEvent(textEvent, senderName):
    # Since client's messages can come from various names, it's easier to calculate when it's NOT from them
    # So if a message comes from <senderName> then consider it a received text. Otherwise, no matter what the name is, say it came from client.
    notFromMe = (textEvent.TextSenderName == senderName)
    className = "from-them" if (notFromMe) else "from-me"
    timeClassName = "message-date them" if (notFromMe) else "message-date me"
    contents = textEvent.TextContents
    date = textEvent.DateTime.strftime("%b %d, %Y, %I:%M %p")
    senderName = textEvent.TextSenderName

    html = '<p class="{0}">{1}</p>'.format(className, contents)
    html += '<span class="{0}">{1}</span>'.format(timeClassName, senderName)
    html += '<span class="{0}">{1}</span>'.format(timeClassName, date)
    return html

##############################
# DAILY CALL TABLE
##############################

# Prints out the daily PhoneCall table...
def printDailyPhoneCallTable(phoneEvents):
    # Sort phoneEvents so we print data out in order...
    phoneEvents.sort(key = lambda x: x.DateTime)

    currentDay = 0
    for phoneEvent in phoneEvents:
        # If we are on a new day, print out the day and update (won't work if day is the same in different months)...
        if (phoneEvent.DateTime.day != currentDay):
            print("\n")
            print(phoneEvent.DateTime.strftime("%b %d, %Y"))
            currentDay = phoneEvent.DateTime.day

        durationMinutes = phoneEvent.PhoneDurationSeconds / 60
        print("\t{0: <16} {1: <16} {2:3.1f} minutes".format(phoneEvent.DateTime.strftime("%I:%M %p"), phoneEvent.PhoneCallType, durationMinutes))

##############################
# Main Program
##############################

# Parse the phone and text mesage files...
phoneEvents = parsePhoneCallFile(CALL_HISTORY_FILE_NAME, PHONE_NUMBER)
textEvents = parseTextMessageFile(TEXT_HISTORY_FILE_NAME)

# Merge data into one list and sort by DateTime...
allEvents = phoneEvents + textEvents
allEvents.sort(key = lambda x: x.DateTime)

# Print the daily phone call table...
printDailyPhoneCallTable(phoneEvents)

# Generate the HTML and write to a file...
html = genHTMLForEvents(allEvents, TEXT_SENDER_NAME)
with open(OUTPUT_FILE, "w+", encoding="utf8") as outputFile:
    data = outputFile.read()
    outputFile.seek(0)
    outputFile.write(html)
    outputFile.truncate()
